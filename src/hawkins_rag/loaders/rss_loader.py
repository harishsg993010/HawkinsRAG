"""RSS feed loader implementation."""
import hashlib
from typing import Any, Dict, Optional
from urllib.parse import urlparse
import feedparser
import requests
import logging
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class RSSLoader(BaseLoader):
    """Loader for RSS and Atom feeds."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize RSS loader with optional configuration."""
        super().__init__(config)
        self.config = config or {}
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
        }

    def load(self, source: str) -> Dict[str, Any]:
        """Load and process RSS feed content.

        Args:
            source: URL of the RSS feed

        Returns:
            Dict containing:
                - content: The processed feed content as text
                - meta_data: Dictionary of metadata about the feed
        """
        try:
            # Parse the feed
            logger.info(f"Loading RSS feed from {source}")
            feed = feedparser.parse(source)

            if feed.bozo and feed.bozo_exception:
                raise ValueError(f"Invalid feed format: {str(feed.bozo_exception)}")

            # Extract feed information
            feed_info = feed.feed
            entries = feed.entries

            # Format content
            content_parts = []

            # Add feed title and description
            if hasattr(feed_info, 'title'):
                content_parts.append(f"Feed Title: {feed_info.title}")
            if hasattr(feed_info, 'description'):
                content_parts.append(f"Description: {feed_info.description}")

            # Process entries
            content_parts.append("\n=== Entries ===\n")
            for entry in entries:
                content_parts.append(f"Title: {entry.get('title', 'No title')}")
                if 'author' in entry:
                    content_parts.append(f"Author: {entry['author']}")
                if 'published' in entry:
                    content_parts.append(f"Published: {entry['published']}")
                if 'description' in entry:
                    content_parts.append(f"Description: {entry['description']}")
                if 'link' in entry:
                    content_parts.append(f"Link: {entry['link']}")
                content_parts.append("---")

            content = "\n".join(content_parts)

            # Generate document ID
            doc_id = hashlib.sha256(
                (source + content[:100]).encode()
            ).hexdigest()[:16]

            logger.info(f"Successfully loaded RSS feed: {source}")
            return {
                "content": content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": source,
                    "type": "rss",
                    "feed_title": getattr(feed_info, 'title', None),
                    "feed_link": getattr(feed_info, 'link', None),
                    "feed_updated": getattr(feed_info, 'updated', None),
                    "total_entries": len(entries)
                }
            }

        except Exception as e:
            logger.error(f"Error loading RSS feed: {str(e)}")
            raise ValueError(f"Error loading RSS feed: {str(e)}")