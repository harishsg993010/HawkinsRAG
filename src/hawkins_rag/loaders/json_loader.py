"""JSON document loader implementation."""
import json
import hashlib
from typing import Any, Dict, Optional
from pathlib import Path
import requests
from urllib.parse import urlparse
from ..utils.base import BaseLoader
import logging

logger = logging.getLogger(__name__)

class JsonLoader(BaseLoader):
    """Loader for JSON files and APIs."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize JSON loader with optional configuration."""
        super().__init__(config)
        self.config = config or {}

    def load(self, source: str) -> Dict[str, Any]:
        """Load and process JSON data from file or URL.

        Args:
            source: Path to JSON file or URL

        Returns:
            Dict containing:
                - content: The JSON content as formatted string
                - meta_data: Dictionary of metadata about the content
        """
        try:
            # Check if source is URL
            url = urlparse(source)
            if all([url.scheme, url.netloc]):
                if url.scheme not in ["http", "https"]:
                    raise ValueError("Only HTTP(S) URLs are supported")
                response = requests.get(source)
                response.raise_for_status()
                data = response.json()
                metadata = {
                    "source_type": "url",
                    "url": source,
                    "content_type": response.headers.get('content-type', '')
                }
            else:
                # Treat as local file path
                path = Path(source)
                if not path.exists():
                    raise ValueError(f"JSON file not found: {source}")
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                metadata = {
                    "source_type": "file",
                    "file_path": str(path),
                    "file_size": path.stat().st_size,
                    "modified_time": path.stat().st_mtime
                }

            # Convert JSON to string representation with proper formatting
            if isinstance(data, (dict, list)):
                # Format the JSON content for better readability
                formatted_content = []
                if isinstance(data, dict):
                    for key, value in data.items():
                        formatted_content.append(f"{key}: {json.dumps(value, indent=2)}")
                    content = "\n".join(formatted_content)
                else:
                    content = json.dumps(data, indent=2)

                # Generate document ID
                doc_id = hashlib.sha256(
                    (content + source).encode()
                ).hexdigest()[:16]

                logger.info(f"Successfully loaded JSON from {source}")
                return {
                    "content": content,
                    "meta_data": {
                        "doc_id": doc_id,
                        "source": source,
                        "type": "json",
                        "data_structure": "object" if isinstance(data, dict) else "array",
                        **metadata
                    }
                }
            else:
                raise ValueError("Invalid JSON format: must be object or array")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {str(e)}")
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading JSON: {str(e)}")
            raise ValueError(f"Error loading JSON: {str(e)}")