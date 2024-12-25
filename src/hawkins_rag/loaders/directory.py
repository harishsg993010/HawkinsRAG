"""Directory content loader implementation."""
import hashlib
from pathlib import Path
from typing import Any, List, Optional, Dict
import logging
from ..utils.base import BaseLoader
from ..utils.loader_registry import get_loader

logger = logging.getLogger(__name__)

class DirectoryLoader(BaseLoader):
    """Loader for directory contents."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize directory loader with configuration."""
        super().__init__(config)
        self.config = config or {}
        self.recursive = self.config.get("recursive", True)
        self.extensions = self.config.get("extensions", None)
        self.errors = []

    def load(self, source: str) -> Dict[str, Any]:
        """Load contents from directory.

        Args:
            source: Path to directory

        Returns:
            Dict containing:
                - content: Combined content from all files
                - meta_data: Directory metadata and file stats
        """
        try:
            directory_path = Path(source)
            if not directory_path.is_dir():
                raise ValueError(f"Invalid directory path: {source}")

            logger.info(f"Loading data from directory: {source}")
            processed_files = self._process_directory(directory_path)

            if not processed_files:
                raise ValueError(f"No valid files found in directory: {source}")

            # Format content for better RAG retrieval
            content_parts = []
            file_stats = []

            for file_data in processed_files:
                content = file_data.get("content", "").strip()
                meta = file_data.get("meta_data", {})
                if content:
                    # Create a value field for HawkinsDB frame
                    value = {
                        "file_path": meta.get("file_path", "Unknown"),
                        "type": meta.get("type", "unknown"),
                        "content": content
                    }

                    # Format content with clear section markers and metadata
                    formatted_section = [
                        f"\nFile Information:",
                        f"Path: {value['file_path']}",
                        f"Type: {value['type']}",
                        "\nContent:",
                        content,
                        "\n---\n"
                    ]
                    content_parts.append("\n".join(formatted_section))

                    # Store metadata for stats
                    file_stats.append({
                        "file_path": meta.get("file_path"),
                        "type": meta.get("type"),
                        "size": meta.get("file_size", 0),
                        "modified_time": meta.get("modified_time")
                    })

            combined_content = "\n".join(content_parts)

            # Generate document ID
            doc_id = hashlib.sha256(
                (str(directory_path) + combined_content[:100]).encode()
            ).hexdigest()[:16]

            logger.info(f"Successfully processed directory: {source}")
            return {
                "content": combined_content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": source,
                    "type": "directory",
                    "file_count": len(processed_files),
                    "recursive": self.recursive,
                    "extensions": self.extensions,
                    "total_size": sum(meta["size"] for meta in file_stats),
                    "file_types": list(set(meta["type"] for meta in file_stats)),
                    "processed_files": file_stats,
                    "errors": self.errors if self.errors else None
                }
            }

        except Exception as e:
            logger.error(f"Error loading directory: {str(e)}")
            raise ValueError(f"Error loading directory: {str(e)}")

    def _process_directory(self, directory_path: Path) -> List[Dict[str, Any]]:
        """Process directory contents recursively."""
        processed_files = []
        glob_pattern = "**/*" if self.recursive else "*"

        for file_path in directory_path.glob(glob_pattern):
            if not file_path.is_file() or file_path.name.startswith('.'):
                continue

            # Get file type from extension
            file_type = file_path.suffix.lower()[1:]  # Remove the dot

            # Skip files without extensions or non-matching extensions
            if not file_type:
                self.errors.append(f"Skipped file without extension: {file_path}")
                continue

            if self.extensions and file_type not in self.extensions:
                self.errors.append(f"Skipped file with non-matching extension: {file_path}")
                continue

            try:
                # Get appropriate loader for file type
                loader = get_loader(file_type)
                if not loader:
                    self.errors.append(f"No loader available for file type: {file_type}")
                    continue

                # Load file content
                logger.info(f"Processing file: {file_path}")
                result = loader.load(str(file_path))

                if result and isinstance(result, dict):
                    # Ensure metadata includes file path relative to directory
                    if "meta_data" in result:
                        result["meta_data"]["file_path"] = str(file_path.relative_to(directory_path))
                    processed_files.append(result)
                else:
                    self.errors.append(f"Invalid content from loader for file: {file_path}")

            except Exception as e:
                self.errors.append(f"Error processing {file_path}: {str(e)}")
                continue

        return processed_files

# For backward compatibility and explicit exports
__all__ = ['DirectoryLoader']