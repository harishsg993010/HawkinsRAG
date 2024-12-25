import hashlib
from typing import Any, Dict, List, Optional
from pathlib import Path
from ..utils.loader_registry import BaseLoader

class LocalTextLoader(BaseLoader):
    """Loader for local text files with customizable encoding support."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize local text loader with optional configuration."""
        self.config = config or {}
        self.encodings = self.config.get('encodings', ['utf-8', 'latin-1', 'cp1252'])

    def load(self, source: str) -> Any:
        """Load content from a local text file.

        Args:
            source: Path to text file

        Returns:
            Dict containing document ID and content
        """
        try:
            path = Path(source)
            if not path.exists():
                raise ValueError(f"Text file not found: {source}")

            content = None
            successful_encoding = None
            errors = []

            # Try different encodings
            for encoding in self.encodings:
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        content = f.read().strip()
                    if content:
                        successful_encoding = encoding
                        break
                except UnicodeDecodeError as e:
                    errors.append(f"Failed with {encoding}: {str(e)}")
                    continue

            if not content or not successful_encoding:
                error_msg = "\n".join(errors)
                raise ValueError(
                    f"Unable to decode file with supported encodings: {self.encodings}\n{error_msg}"
                )

            # Generate document ID
            doc_id = hashlib.sha256(
                (str(path) + content).encode()
            ).hexdigest()

            # Extract metadata
            metadata = {
                "file_path": str(path),
                "encoding": successful_encoding,
                "size": path.stat().st_size,
                "modified_time": path.stat().st_mtime,
                "line_count": len(content.splitlines())
            }

            return {
                "doc_id": doc_id,
                "data": [{
                    "content": content,
                    "meta_data": metadata
                }]
            }

        except Exception as e:
            raise ValueError(f"Error loading text file: {str(e)}")