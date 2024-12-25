# HawkinsRAG Loaders

## Overview
HawkinsRAG provides a comprehensive set of loaders for various data sources. Each loader is specialized for specific content types and formats.

## Available Loaders

### Document Loaders
- [Text Loader](./text_loader.md) - Plain text files
- [PDF Loader](./pdf_loader.md) - PDF documents
- [DOCX Loader](./docx_loader.md) - Microsoft Word documents
- [MDX Loader](./mdx_loader.md) - MDX documentation

### Web Content Loaders
- [YouTube Loader](./youtube_loader.md) - YouTube video transcripts
- [Webpage Loader](./webpage_loader.md) - Web pages
- [RSS Loader](./rss_loader.md) - RSS/Atom feeds

### API Integration Loaders
- [GitHub Loader](./github_loader.md) - GitHub repositories
- [Gmail Loader](./gmail_loader.md) - Email content
- [Slack Loader](./slack_loader.md) - Slack messages

### Structured Data Loaders
- [JSON Loader](./json_loader.md) - JSON files and APIs
- [CSV Loader](./csv_loader.md) - CSV files
- [Excel Loader](./excel_loader.md) - Excel spreadsheets

### Database Loaders
- [MySQL Loader](./mysql_loader.md) - MySQL databases
- [PostgreSQL Loader](./postgresql_loader.md) - PostgreSQL databases

### File System Loaders
- [Directory Loader](./directory_loader.md) - Local directories
- [Dropbox Loader](./dropbox_loader.md) - Dropbox files

## Implementing Custom Loaders

To create a custom loader:

1. Inherit from BaseLoader
2. Implement the load method
3. Register the loader

Example:
```python
from hawkins_rag.utils.base import BaseLoader

class CustomLoader(BaseLoader):
    def __init__(self, config=None):
        super().__init__(config)
        self.config = config or {}

    def load(self, source: str) -> Dict[str, Any]:
        # Implementation
        pass
```

## Common Features

All loaders provide:
- Error handling
- Metadata extraction
- Content formatting
- Configuration options

## Error Handling

Loaders implement consistent error handling:
```python
try:
    result = loader.load("source")
except ValueError as e:
    print(f"Loading error: {str(e)}")
```

## Best Practices

1. **Source Validation**
   - Verify source existence/accessibility
   - Check file formats/permissions
   - Validate API credentials

2. **Content Processing**
   - Handle text encoding
   - Process metadata consistently
   - Implement proper chunking

3. **Error Management**
   - Implement retries for APIs
   - Log errors appropriately
   - Provide meaningful error messages

## Configuration Tips

1. **API-based Loaders**
   - Store credentials securely
   - Implement rate limiting
   - Handle token refresh

2. **File-based Loaders**
   - Set appropriate chunk sizes
   - Handle large files efficiently
   - Validate file formats

3. **Database Loaders**
   - Configure connection pooling
   - Handle transaction management
   - Implement query optimization

## Testing

Test your loaders with:
```python
from hawkins_rag import HawkinsRAG

# Initialize RAG
rag = HawkinsRAG()

# Test loader
try:
    result = rag.load_document("source", source_type="custom")
    print("Loader test successful")
except Exception as e:
    print(f"Loader test failed: {str(e)}")
```

## Documentation Template

When documenting a new loader, include:
1. Overview and purpose
2. Configuration options
3. Usage examples
4. Error handling
5. Best practices
6. Testing guidelines
