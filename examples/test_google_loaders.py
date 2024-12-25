"""Test script for Google loaders (Gmail and Google Drive)."""
import os
import logging
from hawkins_rag import HawkinsRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gmail_loader():
    """Test Gmail loader functionality."""
    # Initialize RAG with Gmail configuration
    config = {
        "loader_config": {
            "gmail": {
                "token_path": "gmail_token.pickle",
                "max_results": 10
            }
        }
    }

    try:
        logger.info("Testing Gmail loader...")
        rag = HawkinsRAG(config=config)

        # Test Gmail queries
        test_queries = [
            "subject:Test",
            "from:example@gmail.com",
            "has:attachment"
        ]

        for query in test_queries:
            try:
                logger.info(f"\nLoading emails matching query: {query}")
                result = rag.load_document(query, source_type="gmail")

                if result:
                    logger.info("Successfully loaded emails")
                    logger.info(f"Processing query: What are these emails about?")
                    response = rag.query("What are these emails about?")
                    logger.info(f"Query response: {response}")

            except Exception as e:
                logger.error(f"Error testing query '{query}': {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Gmail loader test failed: {str(e)}")

def test_gdrive_loader():
    """Test Google Drive loader functionality."""
    # Initialize RAG with Google Drive configuration
    config = {
        "loader_config": {
            "gdrive": {
                "token_path": "gdrive_token.pickle"
            }
        }
    }

    try:
        logger.info("\nTesting Google Drive loader...")
        rag = HawkinsRAG(config=config)

        # Note: To get a file or folder ID from Google Drive:
        # 1. Open the file/folder in Google Drive
        # 2. The ID is in the URL after "/d/" or "/folders/"
        # Example: https://drive.google.com/file/d/FILE_ID_HERE/view
        #         https://drive.google.com/drive/folders/FOLDER_ID_HERE
        test_sources = [
            # Replace these with your actual Google Drive file/folder IDs
            "paste_your_document_id_here",  # Single document test
            "paste_your_folder_id_here"     # Folder test
        ]

        for source in test_sources:
            try:
                logger.info(f"\nLoading content from: {source}")
                result = rag.load_document(source, source_type="gdrive")

                if result:
                    logger.info("Successfully loaded Drive content")
                    logger.info(f"Processing query: What is this document about?")
                    response = rag.query("What is this document about?")
                    logger.info(f"Query response: {response}")

            except Exception as e:
                logger.error(f"Error testing source '{source}': {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Google Drive loader test failed: {str(e)}")

def main():
    """Run Google loader tests."""
    logger.info("Starting Google loader tests...")

    # Test Gmail loader
    test_gmail_loader()

    # Test Google Drive loader
    test_gdrive_loader()

    logger.info("\nCompleted Google loader tests")

if __name__ == "__main__":
    main()