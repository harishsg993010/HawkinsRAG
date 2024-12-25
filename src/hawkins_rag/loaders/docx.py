"""DOCX document loader implementation."""
import docx2txt
import hashlib
from typing import Any, Dict, Optional
from pathlib import Path
import logging
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class DocxLoader(BaseLoader):
    """Loader for DOCX files."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize DOCX loader with optional configuration."""
        super().__init__(config)

    def load(self, source: str) -> Dict[str, Any]:
        """Load text content from a DOCX file.

        Args:
            source: Path to the DOCX file

        Returns:
            Dict containing:
                - content: The document content as text
                - meta_data: Dictionary of metadata about the content
        """
        try:
            path = Path(source)
            if not path.exists():
                raise ValueError(f"DOCX file not found: {source}")

            # Extract text content
            content = docx2txt.process(str(path))
            if not content:
                raise ValueError("Empty document or failed to extract content")

            # Clean and format content
            content = content.strip()

            # Generate document ID
            doc_id = hashlib.sha256(
                (str(path) + content[:100]).encode()
            ).hexdigest()[:16]

            logger.info(f"Successfully loaded DOCX: {path.name}")
            return {
                "content": content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": str(path),
                    "type": "docx",
                    "file_name": path.name,
                    "file_size": path.stat().st_size,
                    "modified_time": path.stat().st_mtime
                }
            }

        except Exception as e:
            logger.error(f"Error loading DOCX: {str(e)}")
            raise ValueError(f"Error loading DOCX: {str(e)}")