"""Google Drive content loader implementation."""
import os
import tempfile
import hashlib
from typing import Any, Optional, Dict, List
from pathlib import Path
import logging
from ..utils.base import BaseLoader
from ..utils.google_auth import get_google_oauth_config, initialize_oauth_flow, handle_oauth_error

logger = logging.getLogger(__name__)

class GoogleDriveLoader(BaseLoader):
    """Loader for Google Drive files and folders."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Google Drive loader with OAuth2 credentials."""
        super().__init__(config)
        self.config = config or {}
        self.service = None
        self._initialize_service()

    def _initialize_service(self) -> None:
        """Initialize Google Drive API service with proper authentication."""
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaIoBaseDownload
            import pickle

            # Define scopes
            SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

            # Load or create credentials
            creds = None
            token_path = self.config.get('token_path', 'gdrive_token.pickle')

            # Try to load existing token
            if os.path.exists(token_path):
                logger.info("Loading existing Google Drive credentials...")
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)

            # If no valid credentials available, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired Google Drive credentials...")
                    creds.refresh(Request())
                else:
                    logger.info("Initiating new Google Drive OAuth flow...")
                    creds = initialize_oauth_flow(token_path, SCOPES)
                    if not creds:
                        raise ValueError("Failed to initialize OAuth flow")

            # Create Drive API service
            self.service = build('drive', 'v3', credentials=creds)
            self.MediaIoBaseDownload = MediaIoBaseDownload
            logger.info("Google Drive API service initialized successfully")

        except ImportError as e:
            raise ImportError(
                "Google Drive loader requires extra dependencies. "
                "Install with: pip install google-auth-oauthlib google-api-python-client"
            ) from e
        except Exception as e:
            error_msg = handle_oauth_error(e)
            logger.error(f"Failed to initialize Google Drive service: {error_msg}")
            raise ValueError(f"Google Drive service initialization failed: {error_msg}")

    def _download_file(self, file_id: str, file_name: str, save_path: str) -> Optional[Dict[str, Any]]:
        """Download and process a file from Google Drive."""
        try:
            # Get file metadata first
            file_metadata = self.service.files().get(
                fileId=file_id, 
                fields="id, name, mimeType, createdTime, modifiedTime, size"
            ).execute()

            # Download file content
            request = self.service.files().get_media(fileId=file_id)
            file_path = os.path.join(save_path, file_name)

            with open(file_path, 'wb') as f:
                downloader = self.MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()

            # Read content based on file type
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                logger.warning(f"File {file_name} appears to be binary, skipping content extraction")
                content = f"[Binary file: {file_name}]"

            return {
                "content": content,
                "meta_data": {
                    "file_id": file_id,
                    "name": file_name,
                    "mime_type": file_metadata.get('mimeType', ''),
                    "created_time": file_metadata.get('createdTime', ''),
                    "modified_time": file_metadata.get('modifiedTime', ''),
                    "size": file_metadata.get('size', '0')
                }
            }

        except Exception as e:
            logger.error(f"Error downloading file {file_name}: {str(e)}")
            return None

    def _process_folder(self, folder_id: str, folder_name: str) -> List[Dict[str, Any]]:
        """Process all files in a folder recursively."""
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents",
                fields="files(id, name, mimeType, createdTime, modifiedTime, size)",
                pageSize=1000
            ).execute()

            files = results.get('files', [])
            logger.info(f"Found {len(files)} items in folder {folder_name}")

            processed_files = []
            with tempfile.TemporaryDirectory() as temp_dir:
                for file in files:
                    if file['mimeType'] == 'application/vnd.google-apps.folder':
                        # Recursively process subfolders
                        subfolder_files = self._process_folder(file['id'], file['name'])
                        processed_files.extend(subfolder_files)
                    else:
                        # Skip Google Workspace files that can't be downloaded directly
                        if not file['mimeType'].startswith('application/vnd.google-apps'):
                            result = self._download_file(file['id'], file['name'], temp_dir)
                            if result:
                                processed_files.append(result)

            return processed_files

        except Exception as e:
            logger.error(f"Error processing folder {folder_name}: {str(e)}")
            return []

    def load(self, source: str) -> Dict[str, Any]:
        """Load content from Google Drive folder or file.

        Args:
            source: Google Drive file/folder ID or shared URL

        Returns:
            Dict containing:
                - content: Combined content from all processed files
                - meta_data: File/folder metadata and stats
        """
        try:
            if not self.service:
                self._initialize_service()

            # Extract file/folder ID from source
            file_id = source
            if '/' in source:  # Handle shared URLs
                file_id = source.split('/')[-1].split('?')[0]

            logger.info(f"Loading content from Google Drive ID: {file_id}")

            # Get item metadata
            try:
                item = self.service.files().get(
                    fileId=file_id,
                    fields="id, name, mimeType, createdTime, modifiedTime, size"
                ).execute()
            except Exception as e:
                raise ValueError(f"Invalid Google Drive ID or URL: {str(e)}")

            processed_files = []
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                # Process folder contents
                processed_files = self._process_folder(file_id, item['name'])
                if not processed_files:
                    raise ValueError("No compatible files found in the folder")

                # Combine content from all files
                all_content = []
                for file_data in processed_files:
                    if file_data['content']:
                        all_content.append(
                            f"### File: {file_data['meta_data']['name']}\n\n"
                            f"{file_data['content']}"
                        )

                combined_content = "\n\n=== FILE SEPARATOR ===\n\n".join(all_content)

                # Generate document ID
                doc_id = hashlib.sha256(
                    f"{file_id}-{len(processed_files)}".encode()
                ).hexdigest()[:16]

                return {
                    "content": combined_content,
                    "meta_data": {
                        "doc_id": doc_id,
                        "source": source,
                        "type": "gdrive",
                        "item_type": "folder",
                        "folder_id": file_id,
                        "folder_name": item['name'],
                        "file_count": len(processed_files),
                        "created_time": item.get('createdTime', ''),
                        "modified_time": item.get('modifiedTime', ''),
                        "processed_files": [
                            f['meta_data'] for f in processed_files
                        ]
                    }
                }
            else:
                # Process single file
                with tempfile.TemporaryDirectory() as temp_dir:
                    result = self._download_file(file_id, item['name'], temp_dir)
                    if not result:
                        raise ValueError("Failed to process file")

                    # Generate document ID
                    doc_id = hashlib.sha256(
                        f"{file_id}-{item.get('modifiedTime', '')}".encode()
                    ).hexdigest()[:16]

                    return {
                        "content": result['content'],
                        "meta_data": {
                            "doc_id": doc_id,
                            "source": source,
                            "type": "gdrive",
                            "item_type": "file",
                            **result['meta_data']
                        }
                    }

        except Exception as e:
            logger.error(f"Error loading from Google Drive: {str(e)}")
            raise ValueError(f"Google Drive loader failed: {str(e)}")

# For backward compatibility and explicit exports
__all__ = ['GoogleDriveLoader']