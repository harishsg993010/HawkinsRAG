"""Configuration management for HawkinsRAG."""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration for HawkinsRAG system."""

    # Database settings
    storage_type: str = "sqlite"
    db_path: str = "hawkins_rag.db"
    chunk_size: int = 500

    # API Keys
    openai_api_key: Optional[str] = None
    deepgram_api_key: Optional[str] = None
    github_token: Optional[str] = None
    notion_token: Optional[str] = None
    dropbox_access_token: Optional[str] = None

    # Loader-specific configurations
    loader_config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Load API keys from environment variables."""
        # Load API keys from environment
        self.openai_api_key = (
            self.openai_api_key or 
            os.environ.get("OPENAI_API_KEY")
        )
        self.deepgram_api_key = (
            self.deepgram_api_key or 
            os.environ.get("DEEPGRAM_API_KEY")
        )
        self.github_token = (
            self.github_token or 
            os.environ.get("GITHUB_TOKEN")
        )
        self.notion_token = (
            self.notion_token or 
            os.environ.get("NOTION_TOKEN")
        )
        self.dropbox_access_token = (
            self.dropbox_access_token or 
            os.environ.get("DROPBOX_ACCESS_TOKEN")
        )

        # Set keys in environment for other libraries
        if self.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
        if self.deepgram_api_key:
            os.environ["DEEPGRAM_API_KEY"] = self.deepgram_api_key
        if self.github_token:
            os.environ["GITHUB_TOKEN"] = self.github_token
        if self.notion_token:
            os.environ["NOTION_TOKEN"] = self.notion_token
        if self.dropbox_access_token:
            os.environ["DROPBOX_ACCESS_TOKEN"] = self.dropbox_access_token

        logger.debug("Initialized config with storage_type=%s, db_path=%s", 
                    self.storage_type, self.db_path)

    @classmethod
    def from_dict(cls, config_dict: dict) -> 'Config':
        """Create config from dictionary."""
        valid_keys = cls.__dataclass_fields__.keys()
        filtered_dict = {
            k: v for k, v in config_dict.items() 
            if k in valid_keys
        }
        return cls(**filtered_dict)