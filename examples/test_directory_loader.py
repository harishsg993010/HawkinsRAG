"""Test script for directory loader functionality."""
import logging
import os
from pathlib import Path
import json
from hawkins_rag import HawkinsRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_directory():
    """Create test directory with various file types."""
    test_dir = Path("test_data/directory")
    test_dir.mkdir(parents=True, exist_ok=True)

    # Create test text files
    text_files = {
        "document1.txt": "This is a test document about machine learning.\nIt contains information about neural networks and deep learning.",
        "document2.txt": "Python is a versatile programming language.\nIt's widely used in data science and AI applications.",
        "notes.md": """# Important Notes

## Machine Learning Concepts
- Neural Networks
- Deep Learning
- Reinforcement Learning

## Python Libraries
- TensorFlow
- PyTorch
- Scikit-learn
"""
    }

    for filename, content in text_files.items():
        with open(test_dir / filename, "w", encoding="utf-8") as f:
            f.write(content)

    # Create test JSON file
    json_data = {
        "project": "HawkinsRAG",
        "features": [
            "Directory loading",
            "Multiple file format support",
            "RAG capabilities"
        ],
        "description": "Test JSON file for directory loader testing"
    }

    with open(test_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    return test_dir

def test_directory_loader():
    """Test loading content from a directory."""
    test_dir = None
    try:
        # Create test directory with files
        test_dir = create_test_directory()
        logger.info(f"Created test directory at: {test_dir}")

        # Initialize RAG system
        rag = HawkinsRAG()
        logger.info("Initialized RAG system")

        # Test loading directory
        logger.info(f"\nTesting directory loader with path: {test_dir}")
        try:
            result = rag.load_document(str(test_dir), source_type="directory")
            logger.info(f"Directory loader test: {'SUCCESS' if result else 'FAILED'}")

            if result:
                # Test different queries
                test_queries = [
                    "What topics are covered in these documents?",
                    "What programming languages are mentioned?",
                    "What machine learning concepts are discussed?",
                    "What features are listed in the config file?"
                ]

                for query in test_queries:
                    logger.info(f"\nTesting query: {query}")
                    response = rag.query(query)
                    logger.info(f"Query response: {response}")

        except Exception as e:
            logger.error(f"Error testing directory loader: {str(e)}")

    except Exception as e:
        logger.error(f"Error in directory loader test: {str(e)}")
    finally:
        # Cleanup
        if test_dir and test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)
            logger.info("Cleaned up test directory")

def main():
    """Run directory loader tests."""
    logger.info("Starting directory loader tests...")
    test_directory_loader()
    logger.info("\nCompleted directory loader tests")

if __name__ == "__main__":
    main()