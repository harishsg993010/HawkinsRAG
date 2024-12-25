"""Test script for YouTube and unstructured content loading with HawkinsRAG."""
import logging
import os
from pathlib import Path
from hawkins_rag import HawkinsRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_test_files():
    """Create test files for unstructured loader testing."""
    test_dir = Path("test_data/advanced")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a test markdown file
    md_content = """# Test Document
    
## Section 1
This is a test document for the unstructured loader.

## Section 2
- Point 1: Testing bullet points
- Point 2: Testing formatting
"""
    
    with open(test_dir / "test.md", "w") as f:
        f.write(md_content)
        
    return test_dir

def test_youtube_loader():
    """Test loading content from YouTube."""
    config = {
        "loader_config": {
            "youtube": {
                "api_key": os.getenv("YOUTUBE_API_KEY")
            }
        }
    }
    
    rag = HawkinsRAG(config=config)
    
    # Test with Python's official getting started video
    video_url = "https://www.youtube.com/watch?v=Y8Tko2YC5hA"
    logger.info(f"\nTesting YouTube loader with video: {video_url}")
    
    try:
        result = rag.load_document(video_url, source_type="youtube")
        logger.info(f"YouTube video loader test: {'SUCCESS' if result else 'FAILED'}")
        
        if result:
            query = "What is this video about?"
            response = rag.query(query)
            logger.info(f"Query response: {response}")
    except Exception as e:
        logger.error(f"Error testing YouTube video loader: {str(e)}")

    # Test with Python's official channel
    channel_url = "https://www.youtube.com/c/python"
    logger.info(f"\nTesting YouTube loader with channel: {channel_url}")
    
    try:
        result = rag.load_document(channel_url, source_type="youtube")
        logger.info(f"YouTube channel loader test: {'SUCCESS' if result else 'FAILED'}")
        
        if result:
            query = "What kind of content is on this channel?"
            response = rag.query(query)
            logger.info(f"Query response: {response}")
    except Exception as e:
        logger.error(f"Error testing YouTube channel loader: {str(e)}")

def test_unstructured_loader():
    """Test unstructured content loading."""
    rag = HawkinsRAG()
    
    # Set up test files
    test_dir = setup_test_files()
    logger.info("\nTesting unstructured loader...")
    
    try:
        # Test markdown file
        md_file = test_dir / "test.md"
        logger.info(f"Testing markdown file: {md_file}")
        
        result = rag.load_document(str(md_file), source_type="unstructured")
        logger.info(f"Unstructured loader test (markdown): {'SUCCESS' if result else 'FAILED'}")
        
        if result:
            query = "What are the main sections in the document?"
            response = rag.query(query)
            logger.info(f"Query response: {response}")
            
    except Exception as e:
        logger.error(f"Error testing unstructured loader: {str(e)}")
    finally:
        # Cleanup test files
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir)

def main():
    """Run all tests."""
    logger.info("Starting advanced loader tests...")
    
    # First test YouTube loader
    test_youtube_loader()
    
    # Then test unstructured loader
    test_unstructured_loader()
    
    logger.info("\nCompleted all advanced loader tests")

if __name__ == "__main__":
    main()
