"""HawkinsRAG - A RAG system built on HawkinsDB.

Example usage:
    from hawkins_rag import HawkinsRAG

    # Initialize RAG system
    rag = HawkinsRAG()

    # Load a document (auto-detects type)
    rag.load_document("document.pdf")

    # Query the system
    response = rag.query("What is this document about?")
    print(response)
"""
from .core import HawkinsRAG
from .config import Config

__version__ = "0.1.0"
__all__ = ["HawkinsRAG", "Config"]