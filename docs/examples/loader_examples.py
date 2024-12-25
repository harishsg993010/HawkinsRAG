"""Examples demonstrating various loader configurations and usage patterns."""
import os
import logging
from hawkins_rag import HawkinsRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def youtube_example():
    """Example using YouTube loader."""
    config = {
        "loader_config": {
            "youtube": {
                "api_key": os.getenv("YOUTUBE_API_KEY")
            }
        }
    }
    
    rag = HawkinsRAG(config=config)
    
    # Load a YouTube video
    video_url = "https://www.youtube.com/watch?v=example"
    result = rag.load_document(video_url, source_type="youtube")
    
    # Query video content
    response = rag.query("What is the main topic discussed in this video?")
    print(f"Video content analysis: {response}")

def github_example():
    """Example using GitHub loader."""
    config = {
        "loader_config": {
            "github": {
                "token": os.getenv("GITHUB_TOKEN")
            }
        }
    }
    
    rag = HawkinsRAG(config=config)
    
    # Load repository content
    repo_path = "repo:username/repository/README.md"
    result = rag.load_document(repo_path, source_type="github")
    
    # Analyze repository content
    response = rag.query("What is this repository about?")
    print(f"Repository analysis: {response}")

def directory_example():
    """Example using directory loader with multiple file types."""
    config = {
        "loader_config": {
            "directory": {
                "recursive": True,
                "extensions": ["txt", "pdf", "docx", "md"]
            }
        }
    }
    
    rag = HawkinsRAG(config=config)
    
    # Load all supported files from directory
    result = rag.load_document("project_docs/", source_type="directory")
    
    # Analyze directory content
    response = rag.query("What are the main topics covered in these documents?")
    print(f"Directory content analysis: {response}")

def structured_data_example():
    """Example using structured data loaders."""
    rag = HawkinsRAG()
    
    # Load and analyze JSON data
    result = rag.load_document("data.json", source_type="json")
    json_response = rag.query("What insights can we draw from this JSON data?")
    print(f"JSON analysis: {json_response}")
    
    # Load and analyze CSV data
    result = rag.load_document("data.csv", source_type="csv")
    csv_response = rag.query("What patterns are visible in this CSV data?")
    print(f"CSV analysis: {csv_response}")

def error_handling_example():
    """Example demonstrating error handling."""
    try:
        rag = HawkinsRAG()
        
        # Attempt to load non-existent file
        result = rag.load_document("missing.txt", source_type="text")
    except FileNotFoundError as e:
        print(f"File error: {str(e)}")
    except ValueError as e:
        print(f"Value error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

def main():
    """Run all examples."""
    logger.info("Starting loader examples...")
    
    try:
        youtube_example()
        github_example()
        directory_example()
        structured_data_example()
        error_handling_example()
    except Exception as e:
        logger.error(f"Error in examples: {str(e)}")
    
    logger.info("Completed all examples")

if __name__ == "__main__":
    main()
