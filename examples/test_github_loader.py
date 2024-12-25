"""Test script for GitHub loader functionality."""
import logging
import os
from pathlib import Path
from hawkins_rag import HawkinsRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_github_loader():
    """Test GitHub loader with various content types."""
    # Initialize RAG with GitHub configuration
    config = {
        "loader_config": {
            "github": {
                "token": os.getenv("GITHUB_TOKEN")
            }
        }
    }
    
    rag = HawkinsRAG(config=config)
    
    # Test cases for different GitHub content types
    test_cases = [
        {
            "name": "Repository Code",
            "source": "code:repo:python/cpython filename:README.md",
            "query": "What is this repository about?"
        },
        {
            "name": "Issues",
            "source": "issue:repo:python/cpython is:open label:bug",
            "query": "What are the recent issues about?"
        },
        {
            "name": "Pull Requests",
            "source": "pr:repo:python/cpython is:open label:enhancement",
            "query": "What new features are being proposed?"
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\nTesting {test_case['name']}...")
        try:
            # Load GitHub content
            result = rag.load_document(test_case["source"], source_type="github")
            logger.info(f"GitHub {test_case['name']} loader test: {'SUCCESS' if result else 'FAILED'}")
            
            if result:
                # Test query
                logger.info(f"Testing query: {test_case['query']}")
                response = rag.query(test_case["query"])
                logger.info(f"Query response: {response}")
                
        except Exception as e:
            logger.error(f"Error testing {test_case['name']}: {str(e)}")

def main():
    """Run GitHub loader tests."""
    logger.info("Starting GitHub loader tests...")
    test_github_loader()
    logger.info("\nCompleted GitHub loader tests")

if __name__ == "__main__":
    main()
