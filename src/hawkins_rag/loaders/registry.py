"""Registry for loader implementations."""
from typing import Type, Dict
from .base import BaseLoader
from .pdf import PDFLoader
from .audio import AudioLoader
from .csv import CSVLoader
from .github import GithubLoader
from .notion import NotionLoader
from .beehive import BeehiveLoader
from .discourse import DiscourseLoader
from .docx import DocxLoader
from .dropbox import DropboxLoader
from .excel import ExcelLoader
from .discord import DiscordLoader
from .json_loader import JSONLoader
from .text_loader import TextLoader
from .qna_loader import QnALoader
from .gmail import GmailLoader
from .googledrive import GoogleDriveLoader

LOADER_REGISTRY: Dict[str, Type[BaseLoader]] = {
    "pdf": PDFLoader,
    "audio": AudioLoader,
    "csv": CSVLoader,
    "github": GithubLoader,
    "notion": NotionLoader,
    "beehive": BeehiveLoader,
    "discourse": DiscourseLoader,
    "docx": DocxLoader,
    "dropbox": DropboxLoader,
    "excel": ExcelLoader,
    "discord": DiscordLoader,
    "json": JSONLoader,
    "text": TextLoader,
    "qna": QnALoader,
    "gmail": GmailLoader,
    "gdrive": GoogleDriveLoader,
}

def get_loader(source_type: str) -> BaseLoader:
    """Get appropriate loader for source type."""
    loader_class = LOADER_REGISTRY.get(source_type.lower())
    if not loader_class:
        raise ValueError(f"Unsupported source type: {source_type}")
    return loader_class()

def register_loader(source_type: str, loader_class: Type[BaseLoader]):
    """Register a new loader type."""
    LOADER_REGISTRY[source_type.lower()] = loader_class