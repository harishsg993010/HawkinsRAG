# HawkinsRAG

A Python package for building Retrieval-Augmented Generation (RAG) systems with HawkinsDB and multiple data source integrations.

## Features
- Multiple data source support through specialized loaders
- Efficient text chunking and embedding
- Seamless integration with HawkinsDB
- Flexible configuration options
- Comprehensive error handling

## Installation

```bash
pip install hawkins-rag
```

## Quick Start

```python
from hawkins_rag import HawkinsRAG

# Initialize RAG system
rag = HawkinsRAG()

# Load document
result = rag.load_document("document.txt", source_type="text")

# Query content
response = rag.query("What is this document about?")
print(response)
```

## Supported Data Sources

HawkinsRAG supports multiple data sources through specialized loaders:

- Text files (txt, pdf, docx)
- Web content (YouTube, webpages)
- Structured data (JSON, CSV)
- APIs (GitHub, Gmail, Slack)
- Databases (MySQL, PostgreSQL)
- And many more!

## Configuration

```python
config = {
    "storage_type": "sqlite",  # or "postgres"
    "db_path": "hawkins_rag.db",
    "chunk_size": 500,
    "loader_config": {
        "youtube": {
            "api_key": "YOUR_YOUTUBE_API_KEY"
        },
        "github": {
            "token": "YOUR_GITHUB_TOKEN"
        }
    }
}

rag = HawkinsRAG(config=config)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Documentation

For detailed documentation, visit [HawkinsRAG Documentation](https://github.com/harishsg993010/HawkinsRAG/docs).
