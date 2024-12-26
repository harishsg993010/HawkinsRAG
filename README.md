# HawkinsRAG

A powerful Python package for building production-ready Retrieval-Augmented Generation (RAG) systems. Seamlessly integrate with HawkinsDB and various data sources to enhance your LLM applications.

- Python 3.8+
- MIT License
- Available on PyPI

## ✨ Features

- 🔌 Extensive data source integrations (22+ data sources)
- 🚀 Native HawkinsDB integration

## 🚀 Quick Start

### Installation

```bash
pip install hawkins-rag
```

### Basic Usage

```python
from hawkins_rag import HawkinsRAG

# Initialize RAG system
rag = HawkinsRAG()

# Load and process a document
result = rag.load_document("document.txt", source_type="text")

# Query your content
response = rag.query("What is this document about?")
print(response)
```

## 🔌 Supported Integrations

### Document Formats
- 📄 Text Files (`.txt`)
- 📑 PDF Documents (`.pdf`)
- 📝 Markdown Files (`.md`, `.mdx`)
- 📊 Microsoft Office (`.docx`)
- 📈 Excel Files (`.xlsx`, `.xls`)
- 🔤 JSON Files (`.json`)
- 📊 CSV Files (`.csv`)
- 📋 XML Files (`.xml`)
- 📂 Directory Loading

### Web & APIs
- 🌐 Web Pages & URLs
- 📺 YouTube Videos
- 📱 OpenAPI Specifications
- 📰 RSS Feeds
- 🐝 Beehive Integration
- 💬 Local Text Processing

### Development & Collaboration Tools
- 💻 GitHub Integration
- 💬 Slack Workspace
- 📂 Directory Crawling
- 🔍 Unstructured File Processing
- ❓ Q&A Format Support

### Google Workspace
- 📧 Gmail Integration
- 💾 Google Drive
- 📊 Google Workspace Apps

### Media & Special Formats
- 🎵 Audio Files
- 📝 Q&A Datasets
- 📄 Unstructured Content

## ⚙️ Configuration

```python
config = {
    "storage": {
        "type": "sqlite",  # or "postgres"
        "path": "hawkins_rag.db",
        "connection_string": "postgresql://user:pass@localhost:5432/db"
    },
    "processing": {
        "chunk_size": 500,
        "overlap": 50
    },
    "integrations": {
        "youtube": {
            "api_key": "YOUR_YOUTUBE_API_KEY"
        },
        "github": {
            "token": "YOUR_GITHUB_TOKEN"
        },
        "google": {
            "credentials_path": "path/to/credentials.json"
        }
    }
}

rag = HawkinsRAG(config=config)
```

## 📚 Documentation

For comprehensive documentation, visit our [documentation on GitHub](https://github.com/harishsg993010/HawkinsRAG/tree/main/docs).

## 💡 Examples

For usage examples and code samples, check out our [examples directory](https://github.com/harishsg993010/HawkinsRAG/tree/main/examples).

## 🔄 Advanced Usage

### Custom Data Source Integration

```python
from hawkins_rag import BaseLoader

class CustomLoader(BaseLoader):
    def load(self, source):
        # Implement custom loading logic
        pass

# Register custom loader
rag.register_loader("custom", CustomLoader())
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
