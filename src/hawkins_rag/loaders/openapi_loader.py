"""OpenAPI specification loader implementation."""
import hashlib
import json
import yaml
from typing import Any, Dict, Optional
from pathlib import Path
import requests
from urllib.parse import urlparse
import logging
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class OpenAPILoader(BaseLoader):
    """Loader for OpenAPI specifications (JSON/YAML)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize OpenAPI loader with optional configuration."""
        super().__init__(config)

    def _is_url(self, source: str) -> bool:
        """Check if source is a URL."""
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _load_spec(self, source: str) -> Dict[str, Any]:
        """Load OpenAPI specification from file or URL."""
        try:
            if self._is_url(source):
                response = requests.get(source)
                response.raise_for_status()
                content = response.text
                metadata = {
                    "source_type": "url",
                    "url": source,
                    "content_type": response.headers.get('content-type', '')
                }
            else:
                path = Path(source)
                if not path.exists():
                    raise ValueError(f"Specification file not found: {source}")
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                metadata = {
                    "source_type": "file",
                    "file_path": str(path),
                    "file_size": path.stat().st_size,
                    "modified_time": path.stat().st_mtime
                }

            # Try parsing as JSON first
            try:
                return json.loads(content), metadata
            except json.JSONDecodeError:
                # If not JSON, try YAML
                try:
                    return yaml.safe_load(content), metadata
                except yaml.YAMLError as e:
                    raise ValueError(f"Invalid YAML format: {str(e)}")

        except Exception as e:
            raise ValueError(f"Error loading OpenAPI specification: {str(e)}")

    def load(self, source: str) -> Dict[str, Any]:
        """Load and process OpenAPI specification.

        Args:
            source: Path to OpenAPI spec file or URL

        Returns:
            Dict containing:
                - content: The specification content as text
                - meta_data: Dictionary of metadata about the content
        """
        try:
            # Load and parse specification
            spec, metadata = self._load_spec(source)

            # Validate OpenAPI version
            if 'openapi' not in spec and 'swagger' not in spec:
                raise ValueError("Invalid OpenAPI specification: version not found")

            # Convert spec to string for storage
            content = json.dumps(spec, indent=2)

            # Generate document ID
            doc_id = hashlib.sha256(
                (source + content[:100]).encode()
            ).hexdigest()[:16]

            logger.info(f"Successfully loaded OpenAPI specification from {source}")
            return {
                "content": content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": source,
                    "type": "openapi",
                    "version": spec.get('openapi') or spec.get('swagger'),
                    "title": spec.get('info', {}).get('title', 'Untitled'),
                    "version_info": spec.get('info', {}).get('version', 'Unknown'),
                    **metadata
                }
            }

        except Exception as e:
            logger.error(f"Error loading OpenAPI specification: {str(e)}")
            raise ValueError(f"Error loading OpenAPI specification: {str(e)}")