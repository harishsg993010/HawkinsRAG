"""Registry for loader implementations."""
from typing import Dict, Type, Optional, Any, Callable
from importlib import import_module
import logging
from .base import BaseLoader

logger = logging.getLogger(__name__)

# Global registry to store loader factory functions
_LOADER_REGISTRY: Dict[str, Callable[..., BaseLoader]] = {}

def register_loader(source_type: str, loader_module: str) -> None:
    """Register a new loader type.

    Args:
        source_type: Type identifier for the loader (e.g., 'pdf', 'csv')
        loader_module: Module path relative to hawkins_rag.loaders
    """
    def loader_factory(config: Optional[Dict] = None) -> BaseLoader:
        """Factory function to create loader instances."""
        try:
            module = import_module(f"hawkins_rag.loaders.{loader_module}")
            # Map source types to their loader class names
            class_name_map = {
                'pdf': 'PDFLoader',
                'json': 'JsonLoader',
                'csv': 'CSVLoader',
                'text': 'TextLoader',
                'txt': 'TextLoader',  # Added txt mapping
                'docx': 'DocxLoader',
                'excel': 'ExcelLoader',
                'webpage': 'WebPageLoader',
                'openapi': 'OpenAPILoader',
                'unstructured': 'UnstructuredFileLoader',
                'youtube': 'YouTubeLoader',
                'mdx': 'MdxLoader',
                'md': 'UnstructuredFileLoader',  # Added md mapping
                'local_text': 'LocalTextLoader',
                'xml': 'XMLLoader',
                'rss': 'RSSLoader',
                'beehive': 'BeehiveLoader',
                'github': 'GithubLoader',
                'gmail': 'GmailLoader',
                'gdrive': 'GoogleDriveLoader',
                'audio': 'AudioLoader',
                'qna': 'QnALoader',
                'slack': 'SlackLoader',
                'directory': 'DirectoryLoader'
            }

            class_name = class_name_map.get(source_type.lower())
            if not class_name:
                raise ValueError(f"Unknown loader type: {source_type}")

            loader_class = getattr(module, class_name)
            return loader_class(config=config)
        except ImportError as e:
            logger.error(f"Failed to import loader for {source_type}: {str(e)}")
            raise ImportError(f"Loader for {source_type} not available. Error: {str(e)}")
        except AttributeError as e:
            logger.error(f"Failed to get loader class for {source_type}: {str(e)}")
            raise ValueError(f"Invalid loader configuration for {source_type}")

    _LOADER_REGISTRY[source_type.lower()] = loader_factory

def get_loader(source_type: str, config: Optional[Dict] = None) -> BaseLoader:
    """Get a loader instance for a specific type."""
    source_type = source_type.lower()
    loader_factory = _LOADER_REGISTRY.get(source_type)
    if not loader_factory:
        logger.error(f"No loader registered for type: {source_type}")
        raise ValueError(f"Unknown loader type: {source_type}")
    return loader_factory(config)

# Register built-in loaders
register_loader('youtube', 'youtube_loader')
register_loader('unstructured', 'unstructured_loader')
register_loader('pdf', 'pdf')
register_loader('text', 'text_loader')
register_loader('txt', 'text_loader')  # Added txt loader registration
register_loader('md', 'unstructured_loader')  # Added md loader registration
register_loader('docx', 'docx')
register_loader('json', 'json_loader')
register_loader('csv', 'csv')
register_loader('excel', 'excel')
register_loader('webpage', 'webpage_loader')
register_loader('openapi', 'openapi_loader')
register_loader('mdx', 'mdx_loader')
register_loader('local_text', 'local_text_loader')
register_loader('xml', 'xml_loader')
register_loader('rss', 'rss_loader')
register_loader('beehive', 'beehive')
register_loader('github', 'github')
register_loader('gmail', 'gmail')
register_loader('gdrive', 'googledrive')
register_loader('audio', 'audio')
register_loader('qna', 'qna_loader')
register_loader('directory', 'directory')
register_loader('slack', 'slack_loader')