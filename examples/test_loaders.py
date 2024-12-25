"""Test all available loaders that don't require API keys."""
import os
import logging
from pathlib import Path
import json
import csv
from hawkins_rag import HawkinsRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_files():
    """Create test files for each loader type."""
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Create test text file
    with open(test_dir / "test.txt", "w") as f:
        f.write("This is a test document.\nIt contains multiple lines.\nThis is for testing the text loader.")
    
    # Create test JSON file
    json_data = {
        "title": "Test JSON",
        "content": "This is test content for JSON loader",
        "metadata": {"type": "test", "version": 1.0}
    }
    with open(test_dir / "test.json", "w") as f:
        json.dump(json_data, f, indent=2)
    
    # Create test CSV file
    with open(test_dir / "test.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows([
            ["id", "name", "description"],
            [1, "Test Item 1", "This is a test item"],
            [2, "Test Item 2", "Another test item"]
        ])
    
    # Create test MDX file
    with open(test_dir / "test.mdx", "w") as f:
        f.write("""
# Test MDX Document

This is a test MDX document with some content.

## Section 1
- Point 1
- Point 2

## Section 2
Some more text here.
""")
    
    # Create test OpenAPI file
    with open(test_dir / "test.yaml", "w") as f:
        f.write("""
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths:
  /test:
    get:
      summary: Test endpoint
      responses:
        '200':
          description: Successful response
""")

    return test_dir

def test_loaders():
    """Test each loader with its corresponding test file."""
    try:
        # Create test files
        test_dir = create_test_files()
        
        # Initialize RAG system
        rag = HawkinsRAG()
        logger.info("Initialized RAG system")
        
        # Test each loader
        test_files = {
            "text": test_dir / "test.txt",
            "json": test_dir / "test.json",
            "csv": test_dir / "test.csv",
            "mdx": test_dir / "test.mdx",
            "openapi": test_dir / "test.yaml"
        }
        
        for file_type, file_path in test_files.items():
            logger.info(f"\nTesting {file_type} loader...")
            try:
                result = rag.load_document(str(file_path))
                logger.info(f"{file_type.upper()} loader test: {'SUCCESS' if result else 'FAILED'}")
                
                # Test querying the loaded content
                if result:
                    query = "What is this document about?"
                    response = rag.query(query)
                    logger.info(f"Query response for {file_type}: {response}")
            except Exception as e:
                logger.error(f"Error testing {file_type} loader: {str(e)}")
    
    finally:
        # Cleanup
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir)

if __name__ == "__main__":
    test_loaders()
