"""Test advanced loaders (YouTube, unstructured) with HawkinsRAG."""
import logging
from pathlib import Path
import os
from hawkins_rag import HawkinsRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_youtube_loader():
    """Test YouTube loader with a sample video."""
    # Initialize RAG with YouTube API key configuration
    config = {
        "loader_config": {
            "youtube": {
                "api_key": os.getenv("YOUTUBE_API_KEY")
            }
        }
    }

    rag = HawkinsRAG(config=config)

    # Use Python's official getting started video
    video_url = "https://www.youtube.com/watch?v=Y8Tko2YC5hA"
    logger.info(f"\nTesting YouTube loader with {video_url}")

    try:
        # Load the video content
        result = rag.load_document(video_url)
        logger.info(f"YouTube loader test: {'SUCCESS' if result else 'FAILED'}")

        if result:
            # Test different types of queries to verify RAG functionality
            queries = [
                "What is this video about?",
                "What are the main topics covered?",
                "What is mentioned in the transcript?"
            ]

            for query in queries:
                logger.info(f"\nTesting query: {query}")
                response = rag.query(query)
                logger.info(f"Query response: {response}")

    except Exception as e:
        logger.error(f"Error testing YouTube loader: {str(e)}")

def create_test_files():
    """Create various test files for unstructured loader."""
    test_dir = Path("test_data/unstructured")
    test_dir.mkdir(parents=True, exist_ok=True)

    # Create test markdown file
    md_content = """# Test Document

## Introduction
This is a test document for the unstructured loader.

## Features
- Handles multiple file types
- Extracts text content
- Preserves formatting
    """

    with open(test_dir / "test.md", "w") as f:
        f.write(md_content)

    # Create test HTML file
    html_content = """
    <html>
        <head><title>Test HTML</title></head>
        <body>
            <h1>Test HTML Document</h1>
            <p>This is a paragraph of text.</p>
            <ul>
                <li>List item 1</li>
                <li>List item 2</li>
            </ul>
        </body>
    </html>
    """

    with open(test_dir / "test.html", "w") as f:
        f.write(html_content)

    return test_dir

def test_unstructured_loader():
    """Test unstructured loader with various file types."""
    test_dir = None
    try:
        # Create test files
        test_dir = create_test_files()

        # Initialize RAG system
        rag = HawkinsRAG()
        logger.info("\nTesting unstructured loader...")

        # Test with different file types
        test_files = {
            "markdown": test_dir / "test.md",
            "html": test_dir / "test.html"
        }

        for file_type, file_path in test_files.items():
            logger.info(f"\nTesting {file_type} file: {file_path}")
            try:
                # Load document
                result = rag.load_document(str(file_path), source_type="unstructured")
                logger.info(f"{file_type.upper()} file test: {'SUCCESS' if result else 'FAILED'}")

                if result:
                    # Test queries
                    queries = [
                        "What is this document about?",
                        "What features are mentioned?",
                        "Summarize the main points"
                    ]

                    for query in queries:
                        logger.info(f"\nTesting query: {query}")
                        response = rag.query(query)
                        logger.info(f"Query response: {response}")

            except Exception as e:
                logger.error(f"Error testing {file_type} file: {str(e)}")

    except Exception as e:
        logger.error(f"Error in unstructured loader test: {str(e)}")
    finally:
        # Cleanup
        if test_dir and test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)

def main():
    """Run all advanced loader tests."""
    logger.info("Starting advanced loader tests...")

    # First test YouTube loader
    test_youtube_loader()

    # Then test unstructured loader
    test_unstructured_loader()

    logger.info("\nCompleted all advanced loader tests")

if __name__ == "__main__":
    main()