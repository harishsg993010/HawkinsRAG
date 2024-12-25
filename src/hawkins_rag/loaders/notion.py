import os
import time
import hashlib
from typing import Any, Dict, List, Optional
from .base import BaseLoader

class NotionLoader(BaseLoader):
    """Loader for Notion pages and databases."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Notion loader with OAuth2 credentials."""
        if not config or "token" not in config:
            raise ValueError(
                "NotionLoader requires an integration token. Get one at "
                "https://www.notion.so/my-integrations"
            )

        try:
            from notion_client import Client
            self.client = Client(auth=config["token"])
        except ImportError:
            raise ImportError(
                "Notion client required. Install with: pip install notion-client"
            )

    def _rate_limit_wait(self):
        """Implement rate limiting."""
        time.sleep(0.3)  # Notion API has a rate limit of 3 requests per second

    def _extract_block_content(self, block: Dict[str, Any]) -> str:
        """Extract text content from a block."""
        block_type = block.get("type", "")
        if block_type not in block:
            return ""

        block_data = block[block_type]
        if "rich_text" in block_data:
            return "".join(
                text.get("plain_text", "")
                for text in block_data["rich_text"]
            )
        elif "title" in block_data:
            return "".join(
                text.get("plain_text", "")
                for text in block_data["title"]
            )
        return ""

    def _get_block_children(self, block_id: str) -> List[Dict[str, Any]]:
        """Get all children blocks of a block."""
        blocks = []
        has_more = True
        start_cursor = None

        while has_more:
            response = self.client.blocks.children.list(
                block_id=block_id,
                start_cursor=start_cursor,
            )
            blocks.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")
            self._rate_limit_wait()

        return blocks

    def _process_page(self, page_id: str) -> Dict[str, Any]:
        """Process a Notion page and its content."""
        page = self.client.pages.retrieve(page_id)
        blocks = self._get_block_children(page_id)

        # Extract page properties
        properties = page.get("properties", {})
        title = ""
        for prop in properties.values():
            if prop["type"] == "title":
                title = "".join(
                    text.get("plain_text", "")
                    for text in prop["title"]
                )
                break

        # Process blocks
        content_parts = []
        for block in blocks:
            # Get block content
            block_content = self._extract_block_content(block)
            if block_content:
                content_parts.append(block_content)

            # Process child blocks if they exist
            if block.get("has_children", False):
                child_blocks = self._get_block_children(block["id"])
                for child in child_blocks:
                    child_content = self._extract_block_content(child)
                    if child_content:
                        content_parts.append("  " + child_content)

        content = "\n".join([f"Title: {title}", *content_parts])
        metadata = {
            "page_id": page_id,
            "created_time": page.get("created_time"),
            "last_edited_time": page.get("last_edited_time"),
            "url": page.get("url"),
        }

        return {
            "content": content,
            "meta_data": metadata,
        }

    def _process_database(self, database_id: str) -> List[Dict[str, Any]]:
        """Process a Notion database and its pages."""
        database = self.client.databases.retrieve(database_id)
        pages = []
        has_more = True
        start_cursor = None

        while has_more:
            response = self.client.databases.query(
                database_id=database_id,
                start_cursor=start_cursor,
            )
            for page in response.get("results", []):
                processed_page = self._process_page(page["id"])
                if processed_page:
                    pages.append(processed_page)
                self._rate_limit_wait()

            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        return pages

    def load(self, source: str) -> Any:
        """Load content from Notion page or database."""
        try:
            # Extract ID from URL or direct ID
            if "notion.so/" in source:
                source_id = source.split("notion.so/")[-1].split("?")[0]
                if "-" in source_id:
                    source_id = source_id.split("-")[-1]
            else:
                source_id = source.strip()

            try:
                # Try as page first
                data = [self._process_page(source_id)]
            except Exception:
                # If fails, try as database
                try:
                    data = self._process_database(source_id)
                except Exception as e:
                    raise ValueError(f"Failed to load content: {str(e)}")

            # Generate document ID
            doc_id = hashlib.sha256(
                (source + str(data)).encode()
            ).hexdigest()

            return {
                "doc_id": doc_id,
                "data": data,
            }

        except Exception as e:
            raise ValueError(f"Error loading from Notion: {str(e)}")