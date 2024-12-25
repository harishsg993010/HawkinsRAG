"""XML loader implementation."""
import hashlib
from typing import Any, Dict, Optional
import xml.etree.ElementTree as ET
from pathlib import Path
import requests
from urllib.parse import urlparse
import logging
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class XMLLoader(BaseLoader):
    """Loader for XML files and URLs."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize XML loader with optional configuration."""
        super().__init__(config)
        self.config = config or {}
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
        }

    def _is_url(self, source: str) -> bool:
        """Check if source is a URL."""
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _extract_text(self, element: ET.Element, path: str = "") -> str:
        """Extract text content from XML element recursively.

        Args:
            element: XML element to process
            path: Current XML path (for context)

        Returns:
            str: Formatted text content
        """
        content_parts = []

        # Handle current element
        current_path = f"{path}/{element.tag}" if path else element.tag

        # Process attributes
        if element.attrib:
            for key, value in element.attrib.items():
                content_parts.append(f"{current_path}/@{key}: {value}")

        # Process text content
        if element.text and element.text.strip():
            content_parts.append(f"{current_path}: {element.text.strip()}")

        # Process child elements
        for child in element:
            child_text = self._extract_text(child, current_path)
            if child_text:
                content_parts.append(child_text)

        # Process tail text
        if element.tail and element.tail.strip():
            content_parts.append(element.tail.strip())

        return "\n".join(content_parts)

    def load(self, source: str) -> Dict[str, Any]:
        """Load content from XML file or URL.

        Args:
            source: Path to XML file or URL

        Returns:
            Dict containing:
                - content: The XML content as formatted text
                - meta_data: Dictionary of metadata about the content

        Raises:
            ValueError: If the XML cannot be loaded or parsed
        """
        try:
            # Load XML content
            logger.info(f"Loading XML from {source}")
            if self._is_url(source):
                response = requests.get(source, headers=self.headers)
                response.raise_for_status()
                xml_content = response.text
                metadata = {
                    "source_type": "url",
                    "url": source
                }
            else:
                path = Path(source)
                if not path.exists():
                    raise ValueError(f"XML file not found: {source}")
                with open(path, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                metadata = {
                    "source_type": "file",
                    "file_path": str(path),
                    "file_size": path.stat().st_size,
                    "modified_time": path.stat().st_mtime
                }

            # Parse XML
            try:
                root = ET.fromstring(xml_content)
            except ET.ParseError as e:
                raise ValueError(f"Invalid XML format: {str(e)}")

            # Extract content
            content = self._extract_text(root)
            if not content:
                raise ValueError("No content found in XML")

            # Generate document ID
            doc_id = hashlib.sha256(
                (source + content[:100]).encode()
            ).hexdigest()[:16]

            logger.info(f"Successfully loaded XML from {source}")
            return {
                "content": content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": source,
                    "type": "xml",
                    "root_tag": root.tag,
                    "encoding": root.get("encoding", "utf-8"),
                    **metadata
                }
            }

        except Exception as e:
            logger.error(f"Error loading XML: {str(e)}")
            raise ValueError(f"Error loading XML: {str(e)}")