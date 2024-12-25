"""Beehive loader implementation for scraping web content."""
import hashlib
import requests
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup, Tag
import logging
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class BeehiveLoader(BaseLoader):
    """Loader for Beehive URLs."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Beehive loader with optional configuration."""
        super().__init__(config)
        self.config = config or {}
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 "
                "Safari/537.36"
            )
        }

    def load(self, source: str) -> Dict[str, Any]:
        """Load data from a Beehive URL.

        Args:
            source: The base URL to scrape

        Returns:
            Dict containing:
                - content: The extracted content
                - meta_data: Dictionary of metadata about the content

        Raises:
            ValueError: If the URL cannot be accessed or content cannot be extracted
        """
        try:
            base_url = source.rstrip('/')
            sitemap_url = f"{base_url}/sitemap.xml" if not source.endswith('sitemap.xml') else source

            logger.info(f"Fetching sitemap from {sitemap_url}")
            response = requests.get(sitemap_url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "xml")
            links: List[str] = []

            # Try to find links in standard sitemap format
            for loc in soup.find_all("loc"):
                if loc.parent.name == "url" and "/p/" in loc.text:
                    links.append(loc.text)

            # Fallback to any loc tags with /p/ if no standard format found
            if not links:
                links = [loc.text for loc in soup.find_all("loc") if "/p/" in loc.text]

            if not links:
                raise ValueError(f"No valid content links found in sitemap: {sitemap_url}")

            content_parts = []
            metadata = {
                "base_url": base_url,
                "total_pages": len(links),
                "processed_pages": 0,
                "failed_pages": 0
            }

            # Process each link
            for link in links:
                try:
                    link_data = self._load_link(link)
                    if link_data:
                        content_parts.append(f"\n=== Page: {link} ===\n")
                        content_parts.append(link_data.get("content", ""))
                        metadata["processed_pages"] += 1
                except Exception as e:
                    logger.warning(f"Failed to process link {link}: {str(e)}")
                    metadata["failed_pages"] += 1

            if not content_parts:
                raise ValueError("No content could be extracted from any page")

            # Join all content
            content = "\n".join(content_parts)

            # Generate document ID
            doc_id = hashlib.sha256(
                (base_url + content[:100]).encode()
            ).hexdigest()[:16]

            logger.info(f"Successfully processed {metadata['processed_pages']} pages from {base_url}")
            return {
                "content": content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": base_url,
                    "type": "beehive",
                    **metadata
                }
            }

        except Exception as e:
            logger.error(f"Error processing Beehive site {source}: {str(e)}")
            raise ValueError(f"Error processing Beehive site: {str(e)}")

    def _load_link(self, link: str) -> Optional[Dict[str, Any]]:
        """Load and process a single Beehive link.

        Args:
            link: URL to process

        Returns:
            Optional[Dict]: Content and metadata if successful, None if failed
        """
        try:
            logger.info(f"Processing link: {link}")
            response = requests.get(link, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            content_data = self._extract_content(soup)

            if not any(content_data.values()):
                logger.warning(f"No content extracted from {link}")
                return None

            return {
                "content": self._format_content(content_data),
                "meta_data": {"url": link}
            }

        except Exception as e:
            logger.warning(f"Error processing link {link}: {str(e)}")
            return None

    def _extract_content(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract structured data from BeautifulSoup response.

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            Dict[str, str]: Extracted content by type
        """
        content: Dict[str, str] = {}

        # Extract title
        title_tag = soup.find("h1")
        if isinstance(title_tag, Tag):
            content["title"] = title_tag.get_text(strip=True)

        # Extract description
        desc_tag = soup.find("meta", {"name": "description"})
        if isinstance(desc_tag, Tag) and desc_tag.get("content"):
            content["description"] = desc_tag["content"]

        # Extract main content
        content_div = soup.find("div", {"id": "content-blocks"})
        if isinstance(content_div, Tag):
            content["content"] = content_div.get_text(strip=True)

        return content

    def _format_content(self, content_data: Dict[str, str]) -> str:
        """Format extracted content into a readable string.

        Args:
            content_data: Dictionary of extracted content

        Returns:
            str: Formatted content string
        """
        parts = []
        if "title" in content_data:
            parts.append(f"Title: {content_data['title']}")
        if "description" in content_data:
            parts.append(f"Description: {content_data['description']}")
        if "content" in content_data:
            parts.append(f"Content:\n{content_data['content']}")
        return "\n\n".join(parts)