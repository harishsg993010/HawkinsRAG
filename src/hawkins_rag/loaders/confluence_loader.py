import hashlib
from typing import Any, Dict, List, Optional
from atlassian import Confluence
from .base import BaseLoader

class ConfluenceLoader(BaseLoader):
    """Loader for Confluence pages and spaces."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Confluence loader with configuration.
        
        Required config:
        - url: Confluence instance URL
        - username: Username/email
        - password: API token or password
        """
        if not config or not all(k in config for k in ['url', 'username', 'password']):
            raise ValueError(
                "ConfluenceLoader requires 'url', 'username', and 'password' in config. "
                "Get API token from https://id.atlassian.com/manage/api-tokens"
            )

        try:
            self.confluence = Confluence(
                url=config['url'],
                username=config['username'],
                password=config['password']
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Confluence client: {str(e)}")

    def _clean_content(self, content: str) -> str:
        """Clean HTML content and extract readable text."""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            return soup.get_text(separator='\n', strip=True)
        except Exception:
            # Fallback to simple HTML tag removal if BeautifulSoup is not available
            import re
            clean = re.compile('<.*?>')
            return re.sub(clean, '', content)

    def _get_page_content(self, page_id: str) -> Dict[str, Any]:
        """Get full page content and metadata."""
        page = self.confluence.get_page_by_id(
            page_id,
            expand='body.storage,version,space,ancestors,descendants.page'
        )

        # Extract clean content
        content = self._clean_content(page['body']['storage']['value'])

        # Get comments
        comments = self.confluence.get_page_comments(page_id, expand='body.view')
        formatted_comments = []
        for comment in comments:
            author = comment['author']['displayName']
            created = comment['created']
            body = self._clean_content(comment['body']['view']['value'])
            formatted_comments.append(f"[{created}] {author}: {body}")

        # Combine content
        full_content = [
            f"Title: {page['title']}",
            f"Space: {page['space']['name']}",
            f"Content:\n{content}",
            "\nComments:",
            *formatted_comments
        ]

        return {
            "content": "\n".join(full_content),
            "meta_data": {
                "id": page['id'],
                "title": page['title'],
                "space_key": page['space']['key'],
                "space_name": page['space']['name'],
                "version": page['version']['number'],
                "created": page['created'],
                "creator": page['history']['createdBy']['displayName'],
                "last_modified": page['version']['when'],
                "last_modifier": page['version']['by']['displayName'],
                "ancestor_ids": [a['id'] for a in page.get('ancestors', [])],
                "descendant_ids": [
                    d['id'] for d in page.get('descendants', {}).get('page', {}).get('results', [])
                ]
            }
        }

    def load(self, source: str) -> Any:
        """Load content from Confluence.

        Args:
            source: Space key and optional page title (e.g., "DEMO" or "DEMO:Home Page")

        Returns:
            Dict containing document ID and array of page data
        """
        try:
            space_key = source.split(':')[0]
            page_title = source.split(':', 1)[1] if ':' in source else None

            if page_title:
                # Get single page
                page = self.confluence.get_page_by_title(space_key, page_title)
                if not page:
                    raise ValueError(f"Page not found: {page_title} in space {space_key}")
                
                page_data = self._get_page_content(page['id'])
                
                # Generate document ID
                doc_id = hashlib.sha256(
                    (source + page_data['content']).encode()
                ).hexdigest()

                return {
                    "doc_id": doc_id,
                    "data": [page_data]
                }
            else:
                # Get all pages in space
                pages = self.confluence.get_all_pages_from_space(space_key, limit=100)
                if not pages:
                    raise ValueError(f"No pages found in space: {space_key}")

                data = []
                all_content = []

                for page in pages:
                    page_data = self._get_page_content(page['id'])
                    data.append(page_data)
                    all_content.append(page_data['content'])

                # Generate document ID
                doc_id = hashlib.sha256(
                    (source + "".join(all_content)).encode()
                ).hexdigest()

                return {
                    "doc_id": doc_id,
                    "data": data
                }

        except Exception as e:
            raise ValueError(f"Error loading from Confluence: {str(e)}")
