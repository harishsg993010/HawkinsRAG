"""MDX (Markdown with JSX) loader implementation."""
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import re
import logging
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class MdxLoader(BaseLoader):
    """Loader for MDX (Markdown with JSX) files."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize MDX loader with optional configuration."""
        super().__init__(config)
        self.jsx_pattern = re.compile(r'<[^>]+>')
        self.frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

    def _extract_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """Extract frontmatter from MDX content."""
        frontmatter: Dict[str, Any] = {}
        match = self.frontmatter_pattern.match(content)

        if match:
            try:
                import yaml
                frontmatter = yaml.safe_load(match.group(1)) or {}
                content = content[match.end():]
            except Exception as e:
                logger.error(f"Failed to parse frontmatter: {str(e)}")
                frontmatter = {"error": f"Failed to parse frontmatter: {str(e)}"}

        return frontmatter, content

    def _extract_jsx_components(self, content: str) -> List[str]:
        """Extract JSX component references from content."""
        components = []
        for match in self.jsx_pattern.finditer(content):
            component = match.group(0)
            if not component.startswith('</'):  # Skip closing tags
                components.append(component)
        return components

    def _clean_content(self, content: str) -> str:
        """Clean MDX content by removing JSX components."""
        # Replace JSX components with placeholders
        content = self.jsx_pattern.sub('[Component]', content)
        return content.strip()

    def load(self, source: str) -> Dict[str, Any]:
        """Load and process MDX file content.

        Args:
            source: Path to MDX file

        Returns:
            Dict containing:
                - content: The cleaned MDX content as text
                - meta_data: Dictionary of metadata about the content
        """
        try:
            path = Path(source)
            if not path.exists():
                raise ValueError(f"MDX file not found: {source}")

            # Read content
            with open(path, 'r', encoding='utf-8') as f:
                raw_content = f.read()

            if not raw_content.strip():
                raise ValueError("Empty MDX file")

            # Extract frontmatter
            frontmatter, content = self._extract_frontmatter(raw_content)

            # Extract JSX components
            components = self._extract_jsx_components(content)

            # Clean content
            cleaned_content = self._clean_content(content)

            if not cleaned_content:
                raise ValueError("No content found after cleaning MDX")

            # Generate document ID
            doc_id = hashlib.sha256(
                (str(path) + cleaned_content[:100]).encode()
            ).hexdigest()[:16]

            logger.info(f"Successfully loaded MDX file: {path.name}")
            return {
                "content": cleaned_content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": str(path),
                    "type": "mdx",
                    "file_name": path.name,
                    "file_size": path.stat().st_size,
                    "frontmatter": frontmatter,
                    "components": components,
                    "modified_time": path.stat().st_mtime
                }
            }

        except Exception as e:
            logger.error(f"Error loading MDX file: {str(e)}")
            raise ValueError(f"Error loading MDX file: {str(e)}")