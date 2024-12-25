"""Loader implementations for various data sources."""
from ..utils.base import BaseLoader
from .pdf import PDFLoader
from .audio import AudioLoader
from .csv import CSVLoader
from .github import GithubLoader
from .notion import NotionLoader
from .directory import DirectoryLoader
from .discord import DiscordLoader
from .beehive import BeehiveLoader
from .discourse import DiscourseLoader
from .docx import DocxLoader
from .dropbox import DropboxLoader
from .excel import ExcelLoader
from .json_loader import JsonLoader
from .text_loader import TextLoader
from .qna_loader import QnALoader
from .gmail import GmailLoader
from .googledrive import GoogleDriveLoader
from .slack_loader import SlackLoader  # Added import
from .webpage_loader import WebPageLoader
from .youtube_loader import YouTubeLoader
from .xml_loader import XMLLoader
from .rss_loader import RSSLoader
from .mysql_loader import MySQLLoader
from .postgresql_loader import PostgreSQLLoader
from .unstructured_loader import UnstructuredFileLoader
from .openapi_loader import OpenAPILoader
from .mdx_loader import MdxLoader
from .local_text_loader import LocalTextLoader
from .jira_loader import JiraLoader
from .confluence_loader import ConfluenceLoader

__all__ = [
    "BaseLoader",
    "PDFLoader",
    "AudioLoader", 
    "CSVLoader",
    "DirectoryLoader",
    "GithubLoader",
    "NotionLoader",
    "DiscordLoader",
    "BeehiveLoader",
    "DiscourseLoader",
    "DocxLoader",
    "DropboxLoader", 
    "ExcelLoader",
    "JsonLoader",  
    "TextLoader",
    "QnALoader",
    "GmailLoader",
    "GoogleDriveLoader",
    "SlackLoader",  # Added to exports
    "WebPageLoader",
    "YouTubeLoader",
    "XMLLoader",
    "RSSLoader",
    "MySQLLoader",
    "PostgreSQLLoader",
    "UnstructuredFileLoader",
    "OpenAPILoader", 
    "MdxLoader",
    "LocalTextLoader",
    "JiraLoader",
    "ConfluenceLoader"
]