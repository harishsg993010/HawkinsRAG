"""Unstructured document loader implementation."""
import hashlib
from typing import Any, Dict, Optional
from pathlib import Path
import logging
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class UnstructuredFileLoader(BaseLoader):
    """Loader for various file formats using unstructured library."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize unstructured loader with optional configuration."""
        super().__init__(config)
        self.config = config or {}
        try:
            from unstructured.partition.auto import partition
            self.partition = partition
            logger.info("Unstructured loader initialized successfully")
        except ImportError:
            logger.error("unstructured package not installed")
            raise ImportError(
                "unstructured package required. Install with: "
                "pip install unstructured"
            )

    def load(self, source: str) -> Dict[str, Any]:
        """Load content from various file formats.

        Args:
            source: Path to the file

        Returns:
            Dict containing:
                - content: The extracted text content
                - meta_data: Dictionary of metadata about the content

        Raises:
            ValueError: If the file cannot be loaded or processed
        """
        try:
            path = Path(source)
            if not path.exists():
                raise ValueError(f"File not found: {source}")

            logger.info(f"Processing file: {source}")

            # Extract content using unstructured
            elements = self.partition(str(path))
            if not elements:
                raise ValueError(f"No content extracted from file: {source}")

            # Combine all text elements with proper formatting
            content_parts = []
            for element in elements:
                text = str(element).strip()
                if text:
                    content_parts.append(text)

            content = "\n\n".join(content_parts)

            # Generate document ID
            doc_id = hashlib.sha256(
                (str(path) + content[:100]).encode()
            ).hexdigest()[:16]

            # Extract metadata
            metadata = {
                "source": str(path),
                "file_type": path.suffix.lower()[1:],
                "file_size": path.stat().st_size,
                "modified_time": path.stat().st_mtime,
                "number_of_elements": len(elements)
            }

            logger.info(f"Successfully processed file: {source}")
            return {
                "content": content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": source,
                    "type": "unstructured",
                    **metadata
                }
            }

        except Exception as e:
            logger.error(f"Error loading file with unstructured: {str(e)}")
            raise ValueError(f"Error loading file with unstructured: {str(e)}")