"""Text file loader implementation."""
import hashlib
from typing import Any, Dict, Optional
from pathlib import Path
import logging
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class TextLoader(BaseLoader):
    """Loader for plain text files."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize text loader with optional configuration."""
        super().__init__(config)
        self.config = config or {}

    def load(self, source: str) -> Dict[str, Any]:
        """Load and process text file.

        Args:
            source: Path to text file

        Returns:
            Dict containing:
                - content: The text content
                - meta_data: Dictionary of metadata about the content
        """
        try:
            path = Path(source)
            if not path.exists():
                raise ValueError(f"Text file not found: {source}")

            logger.info(f"Loading text file: {source}")

            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            content = None
            used_encoding = None

            for encoding in encodings:
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        content = f.read()
                    if content and content.strip():
                        used_encoding = encoding
                        break
                except UnicodeDecodeError:
                    continue

            if not content or not content.strip():
                raise ValueError("Empty or unreadable text file")

            # Generate document ID
            doc_id = hashlib.sha256(
                (str(path) + content[:100]).encode()
            ).hexdigest()[:16]

            logger.info(f"Successfully loaded text file: {source}")
            return {
                "content": content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": source,
                    "type": "text",
                    "file_path": str(path),
                    "file_size": path.stat().st_size,
                    "encoding": used_encoding,
                    "modified_time": path.stat().st_mtime
                }
            }

        except Exception as e:
            logger.error(f"Error loading text file: {str(e)}")
            raise ValueError(f"Error loading text file: {str(e)}")

# For backward compatibility and explicit exports
__all__ = ['TextLoader']