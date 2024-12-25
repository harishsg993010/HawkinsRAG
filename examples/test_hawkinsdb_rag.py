"""Test script for HawkinsDB repository RAG implementation."""
import logging
import os
import time
from typing import Optional
from hawkins_rag import HawkinsRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_github_connection(rag: HawkinsRAG) -> Optional[str]:
    """Test GitHub connection and return error message if any."""
    try:
        # Try loading a small file first to test connection
        test_file = "repo:harishsg993010/HawkinsDB/README.md"
        logger.info("Testing GitHub connection...")
        result = rag.load_document(test_file, source_type="github")
        if result:
            logger.info("GitHub connection test successful")
            return None
        return "Failed to load test file"
    except Exception as e:
        logger.error(f"GitHub connection test failed: {str(e)}")
        return str(e)

def test_hawkinsdb_rag():
    """Test RAG system with HawkinsDB repository."""
    # Initialize RAG with GitHub configuration
    config = {
        "loader_config": {
            "github": {
                "token": os.getenv("GITHUB_TOKEN")
            }
        }
    }

    try:
        logger.info("Initializing RAG system...")
        rag = HawkinsRAG(config=config)

        # Test GitHub connection first
        error = test_github_connection(rag)
        if error:
            logger.error(f"GitHub connection failed: {error}")
            return

        # Test cases for different content types
        test_cases = [
            {
                "name": "Repository README",
                "source": "repo:harishsg993010/HawkinsDB/README.md",
                "queries": [
                    "What is HawkinsDB?",
                    "How do I install HawkinsDB?",
                    "What are the available storage options?"
                ]
            },
            {
                "name": "Core Implementation",
                "source": "repo:harishsg993010/HawkinsDB/src/hawkinsdb/core.py",
                "queries": [
                    "What are the main classes in HawkinsDB?",
                    "How does data storage work?",
                    "What are the key features?"
                ]
            }
        ]

        for test_case in test_cases:
            logger.info(f"\nTesting {test_case['name']}...")
            try:
                # Load GitHub content
                logger.info(f"Loading content from: {test_case['source']}")
                start_time = time.time()
                result = rag.load_document(test_case["source"], source_type="github")
                load_time = time.time() - start_time

                if result:
                    logger.info(f"Successfully loaded content from {test_case['source']} in {load_time:.2f} seconds")

                    # Test queries
                    for query in test_case["queries"]:
                        logger.info(f"\nTesting query: {query}")
                        try:
                            start_time = time.time()
                            response = rag.query(query)
                            query_time = time.time() - start_time
                            logger.info(f"Query completed in {query_time:.2f} seconds")
                            logger.info(f"Response: {response}")
                        except Exception as e:
                            logger.error(f"Error querying: {str(e)}")
                else:
                    logger.error(f"Failed to load content from {test_case['source']}")

            except Exception as e:
                logger.error(f"Error testing {test_case['name']}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Error initializing RAG system: {str(e)}")

def main():
    """Run HawkinsDB RAG tests."""
    logger.info("Starting HawkinsDB RAG tests...")
    test_hawkinsdb_rag()
    logger.info("\nCompleted HawkinsDB RAG tests")

if __name__ == "__main__":
    main()