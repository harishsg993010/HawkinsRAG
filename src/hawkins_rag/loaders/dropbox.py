import os
from typing import Any
from pathlib import Path
import tempfile
from .base import BaseLoader

class DropboxLoader(BaseLoader):
    """Loader for Dropbox content."""

    def __init__(self):
        if not os.environ.get("DROPBOX_ACCESS_TOKEN"):
            raise ValueError("DROPBOX_ACCESS_TOKEN environment variable required")

        try:
            from dropbox import Dropbox
            self.client = Dropbox(os.environ["DROPBOX_ACCESS_TOKEN"])
        except ImportError:
            raise ImportError("dropbox package required. Install with: pip install dropbox")

    def load(self, source: str) -> Any:
        """Load content from Dropbox path."""
        try:
            # Import here to avoid circular dependency
            from .directory import DirectoryLoader

            if source.startswith("/"):
                source = source[1:]

            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                self._download_content(source, temp_dir)

                # Use DirectoryLoader to process downloaded content
                dir_loader = DirectoryLoader()
                content = dir_loader.load(temp_dir)

                return content

        except Exception as e:
            raise ValueError(f"Error loading from Dropbox: {str(e)}")

    def _download_content(self, dbx_path: str, local_dir: str):
        """Download content from Dropbox preserving structure."""
        try:
            result = self.client.files_list_folder(dbx_path)

            for entry in result.entries:
                local_path = Path(local_dir) / entry.name

                if hasattr(entry, "is_dir") and entry.is_dir:
                    local_path.mkdir(exist_ok=True)
                    self._download_content(entry.path_display, str(local_path))
                else:
                    with open(local_path, "wb") as f:
                        metadata, response = self.client.files_download(entry.path_display)
                        f.write(response.content)

        except Exception as e:
            raise ValueError(f"Error downloading from Dropbox: {str(e)}")