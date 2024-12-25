"""Gmail content loader implementation."""
import os
import hashlib
from typing import Any, Optional, Dict
from base64 import urlsafe_b64decode
import logging
from ..utils.base import BaseLoader
from ..utils.google_auth import get_google_oauth_config, initialize_oauth_flow, handle_oauth_error

logger = logging.getLogger(__name__)

class GmailLoader(BaseLoader):
    """Loader for Gmail messages with OAuth2 authentication."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Gmail loader with OAuth2 credentials."""
        super().__init__(config)
        self.config = config or {}
        self.service = None
        self._initialize_service()

    def _initialize_service(self) -> None:
        """Initialize Gmail API service with proper authentication."""
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            import pickle

            # Define scopes
            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

            # Load or create credentials
            creds = None
            token_path = self.config.get('token_path', 'gmail_token.pickle')

            # Try to load existing token
            if os.path.exists(token_path):
                logger.info("Loading existing Gmail credentials...")
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)

            # If no valid credentials available, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired Gmail credentials...")
                    creds.refresh(Request())
                else:
                    logger.info("Initiating new Gmail OAuth flow...")
                    creds = initialize_oauth_flow(token_path, SCOPES)
                    if not creds:
                        raise ValueError("Failed to initialize OAuth flow")

            # Create Gmail API service
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API service initialized successfully")

        except ImportError as e:
            raise ImportError(
                "Gmail loader requires extra dependencies. "
                "Install with: pip install google-auth-oauthlib google-api-python-client"
            ) from e
        except Exception as e:
            error_msg = handle_oauth_error(e)
            logger.error(f"Failed to initialize Gmail service: {error_msg}")
            raise ValueError(f"Gmail service initialization failed: {error_msg}")

    def _decode_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Decode Gmail message content with improved handling."""
        try:
            if 'payload' not in message:
                return {"content": "", "headers": {}}

            payload = message['payload']
            headers = {
                header['name'].lower(): header['value']
                for header in payload.get('headers', [])
            }

            parts = [payload]
            content_parts = []
            attachments = []

            while parts:
                part = parts.pop()
                if 'parts' in part:
                    parts.extend(part['parts'])
                elif 'body' in part:
                    mimeType = part.get('mimeType', '')
                    if 'data' in part['body']:
                        data = urlsafe_b64decode(
                            part['body']['data'].encode('ASCII')
                        ).decode('utf-8', errors='replace')

                        if 'text' in mimeType:
                            content_parts.append(data)
                    elif 'attachmentId' in part['body']:
                        attachments.append({
                            'id': part['body']['attachmentId'],
                            'filename': part.get('filename', ''),
                            'mimeType': mimeType
                        })

            content = "\n".join(content_parts) if content_parts else "No content"

            return {
                "content": content,
                "headers": headers,
                "has_attachments": bool(attachments),
                "attachment_count": len(attachments)
            }
        except Exception as e:
            logger.error(f"Error decoding message: {str(e)}")
            return {"content": "", "headers": {}, "error": str(e)}

    def load(self, source: str) -> Dict[str, Any]:
        """Load Gmail messages matching the search query.

        Args:
            source: Gmail search query (e.g., 'from:example@gmail.com')

        Returns:
            Dict containing:
                - content: Processed email content
                - meta_data: Email metadata and stats
        """
        try:
            if not self.service:
                self._initialize_service()

            # Search for messages
            logger.info(f"Searching Gmail with query: {source}")
            results = self.service.users().messages().list(
                userId='me',
                q=source,
                maxResults=self.config.get('max_results', 100)
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                logger.warning("No messages found matching the query")
                return {
                    "content": "",
                    "meta_data": {
                        "query": source,
                        "message_count": 0,
                        "type": "gmail"
                    }
                }

            # Process messages
            all_content = []
            processed_messages = []

            for msg in messages:
                try:
                    # Get full message details
                    full_msg = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()

                    # Decode message content
                    decoded = self._decode_message(full_msg)
                    if decoded['content']:
                        all_content.append(decoded['content'])
                        processed_messages.append({
                            "message_id": msg['id'],
                            "thread_id": full_msg.get('threadId'),
                            "headers": decoded['headers'],
                            "has_attachments": decoded.get('has_attachments', False),
                            "attachment_count": decoded.get('attachment_count', 0),
                            "labels": full_msg.get('labelIds', []),
                            "date": decoded['headers'].get('date'),
                            "snippet": full_msg.get('snippet', '')
                        })

                except Exception as e:
                    logger.warning(f"Error processing message {msg['id']}: {str(e)}")
                    continue

            if not all_content:
                raise ValueError("Failed to extract content from any messages")

            # Create combined content with clear separation
            combined_content = "\n\n===== EMAIL SEPARATOR =====\n\n".join(all_content)

            # Generate document ID
            doc_id = hashlib.sha256(
                (source + combined_content[:100]).encode()
            ).hexdigest()[:16]

            logger.info(f"Successfully processed {len(processed_messages)} Gmail messages")
            return {
                "content": combined_content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": source,
                    "type": "gmail",
                    "message_count": len(processed_messages),
                    "query": source,
                    "messages": processed_messages
                }
            }

        except Exception as e:
            logger.error(f"Error loading Gmail messages: {str(e)}")
            raise ValueError(f"Gmail loader failed: {str(e)}")

# For backward compatibility and explicit exports
__all__ = ['GmailLoader']