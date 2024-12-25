"""Main RAG system implementation using HawkinsDB."""
import logging
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import mimetypes
import os
from hawkinsdb import HawkinsDB, LLMInterface
from .config import Config
from .utils.loader_registry import get_loader
from .utils import chunk_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HawkinsRAG:
    """Main RAG system implementation using HawkinsDB."""

    def __init__(self, config: Optional[Union[Dict[str, Any], Config]] = None):
        """Initialize the RAG system with optional configuration."""
        try:
            self.config = config if isinstance(config, Config) else Config()
            if isinstance(config, dict):
                self.config = Config.from_dict(config)

            # Initialize HawkinsDB with config
            self.db = HawkinsDB(
                storage_type=self.config.storage_type,
                db_path=self.config.db_path
            )
            self.llm_interface = LLMInterface(self.db, auto_enrich=True)
            self.chunk_size = self.config.chunk_size

            # Ensure YouTube API key is available in loader config
            if 'YOUTUBE_API_KEY' in os.environ:
                if not self.config.loader_config:
                    self.config.loader_config = {}
                self.config.loader_config['youtube'] = {
                    'api_key': os.environ['YOUTUBE_API_KEY']
                }

            logger.info("Initialized HawkinsRAG with config: %s", self.config)
        except Exception as e:
            logger.error("Failed to initialize HawkinsRAG: %s", str(e))
            raise RuntimeError(f"Failed to initialize RAG system: {str(e)}")

    def load_document(self, source: Union[str, List[str]], source_type: Optional[str] = None) -> bool:
        """Load a document or multiple documents into the RAG system.

        Args:
            source: Path to file, URL, or list of sources
            source_type: Optional type of source. If not provided, will be auto-detected

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValueError: If source is invalid or cannot be processed
            RuntimeError: If there's an error during document loading
        """
        try:
            if isinstance(source, list):
                results = []
                for s in source:
                    try:
                        result = self.load_document(s)
                        results.append(result)
                        logger.info(f"Loaded document: {s}")
                    except Exception as e:
                        logger.error(f"Failed to load document {s}: {str(e)}")
                        results.append(False)
                return any(results)  # Return True if at least one document was loaded

            logger.info(f"Loading document: {source}")
            detected_type = source_type or self._detect_source_type(source)
            logger.debug(f"Detected source type: {detected_type}")

            try:
                loader = get_loader(detected_type, self.config.loader_config.get(detected_type))
            except ValueError as e:
                logger.error(f"Invalid loader type: {str(e)}")
                return False

            try:
                content = loader.load(source)
            except Exception as e:
                logger.error(f"Loader failed: {str(e)}")
                return False

            # Create document metadata
            doc_name = Path(source).name if Path(source).exists() else source
            doc_metadata = {
                "name": doc_name,
                "column": "Semantic",
                "properties": {
                    "source": source,
                    "type": detected_type
                }
            }

            # Store document and chunks with error handling
            try:
                self.db.add_entity(doc_metadata)
                chunks = chunk_text(content, doc_name, self.chunk_size)
                for chunk in chunks:
                    self.db.add_entity(chunk)
                logger.info(f"Successfully stored document and {len(chunks)} chunks")
                return True
            except Exception as e:
                logger.error(f"Failed to store document or chunks: {str(e)}")
                return False

        except Exception as e:
            logger.error(f"Error in load_document: {str(e)}")
            return False

    def query(self, question: str) -> Dict[str, Any]:
        """Query the knowledge base with a natural language question."""
        if not question.strip():
            raise ValueError("Question cannot be empty")

        try:
            logger.info(f"Processing query: {question}")
            result = self.llm_interface.query(question)

            if result.get("success"):
                logger.info("Query processed successfully")
                return result
            else:
                error_msg = f"Query failed: {result.get('message')}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "message": error_msg,
                    "response": None
                }

        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "response": None
            }

    def _detect_source_type(self, source: str) -> str:
        """Detect the type of source based on file extension or URL."""
        try:
            # Check for YouTube URLs first
            if any(x in source.lower() for x in ['youtube.com/watch', 'youtu.be/']):
                return 'youtube'

            # Then check for general web URLs
            if source.startswith(('http://', 'https://')):
                return 'webpage'

            # Finally check file extensions
            ext = Path(source).suffix.lower()[1:]
            type_map = {
                'pdf': 'pdf',
                'docx': 'docx',
                'txt': 'text',
                'md': 'text',
                'json': 'json',
                'csv': 'csv',
                'xlsx': 'excel',
                'yaml': 'openapi',
                'yml': 'openapi',
                'mdx': 'mdx',
                'xml': 'xml',
                'rss': 'rss'
            }

            detected_type = type_map.get(ext)
            if not detected_type:
                logger.warning(f"Unknown file extension: {ext}, falling back to unstructured")
                return 'unstructured'

            return detected_type

        except Exception as e:
            logger.error(f"Error detecting source type: {str(e)}")
            raise ValueError(f"Could not determine source type: {str(e)}")

    @classmethod
    def from_env(cls) -> 'HawkinsRAG':
        """Create a HawkinsRAG instance from environment variables."""
        return cls()