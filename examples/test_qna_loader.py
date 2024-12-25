"""Test script for QnA loader functionality."""
import logging
import os
from pathlib import Path
import json
from hawkins_rag import HawkinsRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_files():
    """Create test QnA files in both JSON and text formats."""
    test_dir = Path("test_data/qna")
    test_dir.mkdir(parents=True, exist_ok=True)

    # Create JSON format QnA file
    json_qna = [
        {
            "question": "What is RAG?",
            "answer": "RAG (Retrieval-Augmented Generation) is a technique that combines retrieval of relevant documents with text generation to create more accurate and contextual responses."
        },
        {
            "question": "How does RAG work?",
            "answer": "RAG works by first retrieving relevant documents or chunks from a knowledge base, then using these retrieved documents as context for generating responses using a language model."
        }
    ]

    with open(test_dir / "test_qna.json", "w", encoding="utf-8") as f:
        json.dump(json_qna, f, indent=2)

    # Create text format QnA file
    text_qna = """Q: What is HawkinsDB?
A: HawkinsDB is a neuroscience-inspired memory layer for LLM applications, designed to provide more human-like information storage and retrieval.

Q: What are the key features of HawkinsDB?
A: HawkinsDB features include:
- Inspired by Jeff Hawkins' Thousand Brains Theory
- Efficient document chunking and storage
- Multiple data source integration support
- Advanced semantic search capabilities"""

    with open(test_dir / "test_qna.txt", "w", encoding="utf-8") as f:
        f.write(text_qna)

    return test_dir

def test_qna_loader():
    """Test QnA loader with different file formats."""
    test_dir = None
    try:
        # Create test files
        test_dir = create_test_files()

        # Initialize RAG system
        logger.info("Initializing RAG system...")
        rag = HawkinsRAG()

        # Test files to process
        test_files = {
            "json": test_dir / "test_qna.json",
            "text": test_dir / "test_qna.txt"
        }

        # Test each format
        for format_type, file_path in test_files.items():
            logger.info(f"\nTesting {format_type.upper()} format QnA file: {file_path}")
            try:
                # Load QnA content
                result = rag.load_document(str(file_path), source_type="qna")
                logger.info(f"QnA {format_type} loader test: {'SUCCESS' if result else 'FAILED'}")

                if result:
                    # Test queries
                    test_queries = [
                        "What is RAG?",
                        "How does RAG work?",
                        "What is HawkinsDB?",
                        "What are the key features of HawkinsDB?"
                    ]

                    for query in test_queries:
                        logger.info(f"\nTesting query: {query}")
                        response = rag.query(query)
                        logger.info(f"Query response: {response}")

            except Exception as e:
                logger.error(f"Error testing {format_type} format: {str(e)}")

    except Exception as e:
        logger.error(f"Error in QnA loader test: {str(e)}")
    finally:
        # Cleanup
        if test_dir and test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)

def main():
    """Run QnA loader tests."""
    logger.info("Starting QnA loader tests...")
    test_qna_loader()
    logger.info("\nCompleted QnA loader tests")

if __name__ == "__main__":
    main()