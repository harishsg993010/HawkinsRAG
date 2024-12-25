# HawkinsRAG Documentation

## Overview
HawkinsRAG is a Python package for building Retrieval-Augmented Generation (RAG) systems with HawkinsDB. It provides a flexible architecture for loading data from various sources and performing efficient information retrieval.

## Features
- Multiple data source support through specialized loaders
- Efficient text chunking and embedding
- Seamless integration with HawkinsDB
- Flexible configuration options
- Comprehensive error handling

## Architecture
```
Data Sources → Loaders → Content Processing → HawkinsDB Storage → Query Processing
     ↓            ↓              ↓                    ↓               ↓
  Files       Format-        Chunking &           Efficient        Semantic
  APIs        specific       Embedding            Storage &        Search &
  DBs         handling                           Indexing         Retrieval
```

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

## Core Components

1. **Loaders**
   - Text files (txt, pdf, docx)
   - Web content (YouTube, webpages)
   - Structured data (JSON, CSV)
   - APIs (GitHub, Gmail, Slack)
   - Databases (MySQL, PostgreSQL)

2. **Content Processing**
   - Text chunking
   - Metadata extraction
   - Format conversion
   - Error handling

3. **Storage & Retrieval**
   - HawkinsDB integration
   - Efficient indexing
   - Semantic search
   - Query optimization

## Documentation Structure

- [Getting Started](./getting_started.md)
- [Configuration Guide](./configuration.md)
- [Loader Reference](./loaders/index.md)
- [API Documentation](./api_reference.md)
- [Examples](../examples/README.md)
- [Best Practices](./best_practices.md)
- [Troubleshooting](./troubleshooting.md)
