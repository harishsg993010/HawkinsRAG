"""Test the simplified user API pattern."""
from hawkins_rag import HawkinsRAG

# Initialize RAG system
rag = HawkinsRAG()

# Load a document (auto-detects type)
rag.load_document("my_doc.pdf")

# Query the system
response = rag.query("What is this document about?")
print(response)
