"""Example of using HawkinsRAG in just a few lines."""
from hawkins_rag import HawkinsRAG

def main():
    # Initialize RAG system (automatically uses environment variables)
    rag = HawkinsRAG()

    # Load a document (type will be auto-detected)
    result = rag.load_document("path/to/your/document.pdf")
    print(f"Document loaded successfully: {result}")

    # Ask questions
    response = rag.query("What is this document about?")
    print(f"Response: {response}")

if __name__ == "__main__":
    main()