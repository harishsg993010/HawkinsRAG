"""Basic usage examples for HawkinsRAG."""
from hawkins_rag import HawkinsRAG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def basic_text_example():
    """Basic example using text loader."""
    # Initialize RAG
    rag = HawkinsRAG()
    
    # Create a sample text file
    with open("sample.txt", "w") as f:
        f.write("""
        Machine Learning Overview
        
        Machine learning is a subset of artificial intelligence that focuses on
        developing systems that can learn from and make decisions based on data.
        Key concepts include:
        - Supervised Learning
        - Unsupervised Learning
        - Reinforcement Learning
        """)
    
    # Load the document
    result = rag.load_document("sample.txt", source_type="text")
    
    # Query the content
    queries = [
        "What is machine learning?",
        "What are the key concepts mentioned?",
        "Explain supervised learning from the text"
    ]
    
    for query in queries:
        response = rag.query(query)
        print(f"\nQuery: {query}")
        print(f"Response: {response}")

def main():
    """Run basic usage examples."""
    logger.info("Starting basic usage examples...")
    basic_text_example()
    logger.info("Completed basic usage examples")

if __name__ == "__main__":
    main()
