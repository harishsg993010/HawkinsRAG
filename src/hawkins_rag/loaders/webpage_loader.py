"""Webpage loader implementation."""
import hashlib
from typing import Any, Dict, Optional
import trafilatura
import requests
import logging
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class WebPageLoader(BaseLoader):
    """Loader for web pages using trafilatura."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize web page loader with optional configuration."""
        super().__init__(config)
        self.config = config or {}
        self.timeout = self.config.get('timeout', 30)
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
        }

    def _extract_metadata(self, downloaded: str) -> Dict[str, Any]:
        """Extract metadata from the downloaded content using BeautifulSoup."""
        try:
            soup = BeautifulSoup(downloaded, 'lxml')
            metadata = {}

            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.text.strip()

            # Extract meta description
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag and desc_tag.get('content'):
                metadata['description'] = desc_tag.get('content', '').strip()

            # Extract meta keywords
            keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            if keywords_tag and keywords_tag.get('content'):
                metadata['keywords'] = keywords_tag.get('content', '').strip()

            # Extract author
            author_tag = soup.find('meta', attrs={'name': 'author'})
            if author_tag and author_tag.get('content'):
                metadata['author'] = author_tag.get('content', '').strip()

            return metadata
        except Exception as e:
            logger.warning(f"Error extracting metadata: {str(e)}")
            return {}

    def load(self, source: str) -> Dict[str, Any]:
        """Load content from a web page.

        Args:
            source: URL of the web page to load

        Returns:
            Dict containing:
                - content: The web page content as text
                - meta_data: Dictionary of metadata about the content

        Raises:
            ValueError: If the webpage cannot be loaded or content cannot be extracted
        """
        try:
            # Download content using requests
            logger.info(f"Downloading content from {source}")
            try:
                response = requests.get(
                    source, 
                    headers=self.headers, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                downloaded = response.text
            except RequestException as e:
                logger.error(f"Failed to fetch webpage: {str(e)}")
                raise ValueError(f"Failed to fetch webpage: {str(e)}")

            if not downloaded:
                raise ValueError(f"No content received from {source}")

            # Extract text content using trafilatura with fallback
            try:
                content = trafilatura.extract(
                    downloaded,
                    include_tables=True,
                    include_links=True,
                    include_images=True,
                    no_fallback=False
                )
            except Exception as e:
                logger.warning(f"Trafilatura extraction failed: {str(e)}, trying fallback")
                content = None

            # Fallback to BeautifulSoup if trafilatura fails
            if not content:
                logger.info("Using BeautifulSoup fallback for content extraction")
                soup = BeautifulSoup(downloaded, 'lxml')
                paragraphs = []

                # Get text from paragraphs
                for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    text = p.get_text(strip=True)
                    if text:
                        paragraphs.append(text)

                content = '\n\n'.join(paragraphs)

            if not content:
                raise ValueError(f"No content could be extracted from {source}")

            # Extract metadata
            metadata = self._extract_metadata(downloaded)

            # Generate document ID
            doc_id = hashlib.sha256(
                (source + content[:100]).encode()
            ).hexdigest()[:16]

            logger.info(f"Successfully loaded webpage: {source}")
            return {
                "content": content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": source,
                    "type": "webpage",
                    **metadata
                }
            }

        except Exception as e:
            logger.error(f"Error loading web page: {str(e)}")
            raise ValueError(f"Error loading web page: {str(e)}")