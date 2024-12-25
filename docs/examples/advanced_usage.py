"""Advanced usage examples for HawkinsRAG."""
import os
from hawkins_rag import HawkinsRAG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def youtube_loader_example():
    """Example using YouTube loader."""
    # Configure RAG with YouTube API key
    config = {
        "loader_config": {
            "youtube": {
                "api_key": os.getenv("YOUTUBE_API_KEY")
            }
        }
    }
    
    rag = HawkinsRAG(config=config)
    
    # Load YouTube video content
    video_url = "https://www.youtube.com/watch?v=Y8Tko2YC5hA"
    result = rag.load_document(video_url, source_type="youtube")
    
    # Query video content
    queries = [
        "What is the main topic of this video?",
        "Summarize the key points discussed",
        "What technologies are mentioned?"
    ]
    
    for query in queries:
        response = rag.query(query)
        print(f"\nQuery: {query}")
        print(f"Response: {response}")

def directory_loader_example():
    """Example using directory loader with multiple file types."""
    # Configure RAG for directory loading
    config = {
        "loader_config": {
            "directory": {
                "recursive": True,
                "extensions": ["txt", "pdf", "docx"]
            }
        }
    }
    
    rag = HawkinsRAG(config=config)
    
    # Load directory content
    result = rag.load_document("path/to/documents", source_type="directory")
    
    # Query across all documents
    response = rag.query("What are the common themes across all documents?")
    print(f"Cross-document analysis: {response}")

def main():
    """Run advanced usage examples."""
    logger.info("Starting advanced usage examples...")
    
    try:
        youtube_loader_example()
        directory_loader_example()
    except Exception as e:
        logger.error(f"Error in examples: {str(e)}")
    
    logger.info("Completed advanced usage examples")

if __name__ == "__main__":
    main()
