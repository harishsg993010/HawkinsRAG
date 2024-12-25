from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseLoader(ABC):
    """Base class for all document loaders."""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize loader with optional configuration."""
        self.config = config or {}

    @abstractmethod
    def load(self, source: str) -> Dict[str, Any]:
        """Load data from source.

        Args:
            source: Path or URL to load data from

        Returns:
            Dict containing:
                - content: The main content
                - meta_data: Dictionary of metadata about the content
        """
        pass