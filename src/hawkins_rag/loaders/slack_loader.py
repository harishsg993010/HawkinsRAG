"""Slack loader implementation for loading messages and channels."""
import os
import hashlib
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class SlackLoader(BaseLoader):
    """Loader for Slack messages and channels."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Slack loader with OAuth token."""
        super().__init__(config)
        self.config = config or {}

        if 'token' not in self.config:
            raise ValueError(
                "SlackLoader requires a bot token in config['token']. "
                "Create one at https://api.slack.com/apps"
            )

        try:
            from slack_sdk import WebClient
            from slack_sdk.errors import SlackApiError
            self.client = WebClient(token=self.config['token'])
            self.SlackApiError = SlackApiError
            logger.info("Slack client initialized successfully")
        except ImportError:
            logger.error("slack-sdk package not installed")
            raise ImportError(
                "Slack SDK required. Install with: pip install slack-sdk"
            )

    def _format_message(self, message: Dict[str, Any], thread_replies: Optional[List[Dict[str, Any]]] = None) -> str:
        """Format a Slack message with metadata and thread replies."""
        try:
            timestamp = datetime.fromtimestamp(float(message.get('ts', 0))).isoformat()
            user = message.get('user', 'Unknown')
            text = message.get('text', '')

            formatted = f"[{timestamp}] {user}: {text}"

            # Add thread replies if any
            if thread_replies:
                formatted += "\nThread replies:\n"
                for reply in thread_replies:
                    reply_ts = datetime.fromtimestamp(float(reply.get('ts', 0))).isoformat()
                    reply_user = reply.get('user', 'Unknown')
                    reply_text = reply.get('text', '')
                    formatted += f"  [{reply_ts}] {reply_user}: {reply_text}\n"

            return formatted
        except Exception as e:
            logger.error(f"Error formatting message: {str(e)}")
            return f"Error formatting message: {str(message)}"

    def load(self, source: str) -> Dict[str, Any]:
        """Load content from Slack channel.

        Args:
            source: Channel ID or name (e.g., 'C1234567890' or '#general')

        Returns:
            Dict containing:
                - content: Combined messages content
                - meta_data: Channel and message metadata
        """
        try:
            # Remove # if present in channel name
            channel_id = source.lstrip('#')
            logger.info(f"Loading messages from channel: {channel_id}")

            # Get channel info
            try:
                channel_info = self.client.conversations_info(channel=channel_id)
                if not channel_info['ok']:
                    raise ValueError(f"Invalid channel: {source}")
                logger.info(f"Successfully retrieved channel info for {channel_id}")
            except self.SlackApiError as e:
                logger.error(f"Error getting channel info: {str(e)}")
                raise ValueError(f"Failed to access channel: {str(e)}")

            # Get messages with pagination
            all_messages = []
            cursor = None

            while True:
                try:
                    response = self.client.conversations_history(
                        channel=channel_id,
                        cursor=cursor,
                        limit=100
                    )

                    if not response['ok']:
                        break

                    for msg in response['messages']:
                        # Get thread replies if any
                        thread_replies = []
                        if msg.get('thread_ts'):
                            try:
                                thread = self.client.conversations_replies(
                                    channel=channel_id,
                                    ts=msg['thread_ts']
                                )
                                if thread['ok']:
                                    # Skip the parent message to avoid duplication
                                    thread_replies = thread['messages'][1:]
                            except self.SlackApiError as e:
                                logger.warning(f"Error fetching thread replies: {str(e)}")

                        formatted_content = self._format_message(msg, thread_replies)
                        all_messages.append({
                            "content": formatted_content,
                            "meta_data": {
                                "channel_id": channel_id,
                                "channel_name": channel_info['channel']['name'],
                                "timestamp": msg.get('ts'),
                                "has_thread": bool(thread_replies),
                                "thread_reply_count": len(thread_replies) if thread_replies else 0,
                                "msg_type": msg.get('type', 'unknown')
                            }
                        })

                    # Check for more messages
                    cursor = response.get('response_metadata', {}).get('next_cursor')
                    if not cursor:
                        break

                except self.SlackApiError as e:
                    logger.error(f"Error fetching messages: {str(e)}")
                    break

            if not all_messages:
                raise ValueError(f"No messages found in channel: {source}")

            # Combine all messages with clear separators
            combined_content = "\n\n=== Message {} ===\n".join(
                msg["content"] for msg in all_messages
            ).format(*range(1, len(all_messages) + 1))

            # Generate document ID
            doc_id = hashlib.sha256(
                f"{channel_id}-{len(all_messages)}".encode()
            ).hexdigest()[:16]

            logger.info(f"Successfully loaded {len(all_messages)} messages from {channel_id}")

            return {
                "content": combined_content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": source,
                    "type": "slack",
                    "channel_id": channel_id,
                    "channel_name": channel_info['channel']['name'],
                    "message_count": len(all_messages),
                    "messages": [msg["meta_data"] for msg in all_messages]
                }
            }

        except Exception as e:
            logger.error(f"Error loading from Slack: {str(e)}")
            raise ValueError(f"Slack loader failed: {str(e)}")

# For backward compatibility and explicit exports
__all__ = ['SlackLoader']