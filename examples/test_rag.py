"""Test the minimal RAG interface with a generated PDF."""
from hawkins_rag import HawkinsRAG
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_pdf(filename: str, content: str) -> None:
    """Create a simple PDF file with test content."""
    c = canvas.Canvas(filename, pagesize=letter)
    # Write the content with proper positioning
    c.drawString(100, 750, content)
    # Add some additional content for testing
    c.drawString(100, 700, "This document discusses various concepts in AI.")
    c.drawString(100, 650, "It includes information about machine learning and neural networks.")
    c.showPage()  # Ensure the page is properly created
    c.save()

def main():
    # Create test PDF
    test_content = "This is a test document about artificial intelligence and machine learning."
    test_file = "test_doc.pdf"
    create_test_pdf(test_file, test_content)

    try:
        # Initialize RAG system (using simplified interface)
        logger.info("Initializing RAG system...")
        rag = HawkinsRAG()

        # Load document
        logger.info("Loading document...")
        result = rag.load_document(test_file)
        logger.info(f"Document loaded: {result}")

        # Test query
        test_query = "What is this document about?"
        logger.info(f"Testing query: {test_query}")
        response = rag.query(test_query)
        logger.info(f"Response: {response}")

    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    main()