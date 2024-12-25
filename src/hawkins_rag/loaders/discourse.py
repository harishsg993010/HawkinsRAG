import logging
import time
import hashlib
from typing import Any, Optional, Dict, List
import requests
from .base import BaseLoader

logger = logging.getLogger(__name__)

class DiscourseLoader(BaseLoader):
    """Loader for Discourse content."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if not config or "domain" not in config:
            raise ValueError(
                "DiscourseLoader requires a domain configuration. Example: "
                "{'domain': 'https://discourse.example.com/'}"
            )

        self.domain = config["domain"].rstrip("/") + "/"
        self.api_key = config.get("api_key")
        self.api_username = config.get("api_username")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {}
        if self.api_key and self.api_username:
            headers.update({
                "Api-Key": self.api_key,
                "Api-Username": self.api_username,
            })
        return headers

    def _rate_limit_wait(self):
        """Implement rate limiting."""
        time.sleep(0.5)  # Basic rate limiting

    def load(self, source: str) -> Any:
        """Load content from Discourse search."""
        try:
            if not source:
                raise ValueError("Search query is required for Discourse content")

            # Search for posts
            search_url = f"{self.domain}search.json"
            params = {"q": source}
            headers = self._get_headers()

            response = requests.get(search_url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            if "grouped_search_result" not in data:
                return {
                    "doc_id": hashlib.sha256(source.encode()).hexdigest(),
                    "data": [],
                }

            post_ids = data["grouped_search_result"].get("post_ids", [])
            loaded_data = []

            # Load individual posts
            for post_id in post_ids:
                post_data = self._load_post(post_id)
                if post_data:
                    loaded_data.append(post_data)
                self._rate_limit_wait()

            if not loaded_data:
                logger.warning(f"No posts found for query: {source}")

            # Generate document ID based on source and content
            content_hash = hashlib.sha256(
                (source + str(loaded_data)).encode()
            ).hexdigest()

            return {
                "doc_id": content_hash,
                "data": loaded_data,
            }

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error connecting to Discourse: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading from Discourse: {str(e)}")

    def _load_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Load a single post from Discourse."""
        try:
            post_url = f"{self.domain}posts/{post_id}.json"
            headers = self._get_headers()

            response = requests.get(post_url, headers=headers)
            response.raise_for_status()

            post_data = response.json()

            # Extract topic data if available
            topic_data = {}
            if "topic_slug" in post_data:
                try:
                    topic_url = f"{self.domain}t/{post_data['topic_slug']}/{post_data['topic_id']}.json"
                    topic_response = requests.get(topic_url, headers=headers)
                    topic_response.raise_for_status()
                    topic_data = topic_response.json()
                except Exception as e:
                    logger.warning(f"Failed to load topic data for post {post_id}: {e}")

            # Format post content with metadata
            metadata = {
                "post_id": post_id,
                "post_number": post_data.get("post_number"),
                "created_at": post_data.get("created_at"),
                "updated_at": post_data.get("updated_at"),
                "topic_id": post_data.get("topic_id"),
                "topic_slug": post_data.get("topic_slug"),
                "topic_title": topic_data.get("title"),
                "url": f"{self.domain}t/{post_data['topic_slug']}/{post_data['topic_id']}/{post_data['post_number']}",
            }

            return {
                "content": post_data.get("raw", ""),
                "meta_data": metadata,
            }

        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to load post {post_id}: Network error: {e}")
            return None
        except Exception as e:
            logger.warning(f"Failed to load post {post_id}: {e}")
            return None