# Directory Loader

## Overview
The Directory Loader allows you to process multiple files from a local directory, supporting recursive traversal and multiple file formats.

## Features
- Recursive directory traversal
- Multiple file format support
- Metadata extraction
- Format-specific processing
- Efficient error handling

## Configuration

```python
config = {
    "loader_config": {
        "directory": {
            "recursive": True,  # Enable recursive traversal
            "extensions": ["txt", "pdf", "docx", "md"],  # Supported extensions
            "ignore_errors": False,  # Stop on errors
            "max_files": 1000  # Maximum files to process
        }
    }
}

rag = HawkinsRAG(config=config)
```

## Usage Examples

### Basic Usage
```python
from hawkins_rag import HawkinsRAG

# Initialize RAG
rag = HawkinsRAG()

# Load directory
result = rag.load_document("path/to/directory", source_type="directory")

# Query content
response = rag.query("What topics are covered in these documents?")
print(response)
```

### Advanced Usage
```python
# Configure with specific extensions
config = {
    "loader_config": {
        "directory": {
            "recursive": True,
            "extensions": ["txt", "md"]
        }
    }
}

rag = HawkinsRAG(config=config)

# Load and process
result = rag.load_document("docs/", source_type="directory")

# Multiple queries
queries = [
    "What are the main topics?",
    "List all technical terms",
    "Summarize key findings"
]

for query in queries:
    response = rag.query(query)
    print(f"\nQuery: {query}")
    print(f"Response: {response}")
```

## Output Format

The loader returns:
```python
{
    "content": str,  # Combined content from all files
    "meta_data": {
        "doc_id": str,
        "source": str,
        "type": "directory",
        "file_count": int,
        "recursive": bool,
        "extensions": List[str],
        "total_size": int,
        "file_types": List[str],
        "processed_files": List[Dict],
        "errors": Optional[List[str]]
    }
}
```

## Error Handling

```python
try:
    result = rag.load_document("path/to/directory", source_type="directory")
except ValueError as e:
    print(f"Directory loading error: {str(e)}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

## Best Practices

1. **Directory Structure**
   - Organize files logically
   - Use consistent naming
   - Maintain proper permissions

2. **Performance**
   - Limit directory size
   - Use appropriate extensions
   - Configure chunk size

3. **Error Management**
   - Handle missing files
   - Process format errors
   - Log issues properly

## Implementation Details

The Directory Loader:
1. Validates directory path
2. Lists all files recursively
3. Filters by extension
4. Processes each file
5. Combines content
6. Generates metadata

## Example Implementation

```python
from pathlib import Path
from typing import Dict, Any
from hawkins_rag import HawkinsRAG

def process_directory(directory_path: str) -> Dict[str, Any]:
    """Process all files in a directory."""
    rag = HawkinsRAG(config={
        "loader_config": {
            "directory": {
                "recursive": True,
                "extensions": ["txt", "pdf", "md"]
            }
        }
    })
    
    try:
        # Load directory
        result = rag.load_document(directory_path, source_type="directory")
        
        # Process results
        file_count = result["meta_data"]["file_count"]
        total_size = result["meta_data"]["total_size"]
        print(f"Processed {file_count} files, total size: {total_size} bytes")
        
        # Query content
        summary = rag.query("Summarize the main topics in these documents")
        print(f"Summary: {summary}")
        
        return result
        
    except Exception as e:
        print(f"Error processing directory: {str(e)}")
        raise
```

## Testing

```python
def test_directory_loader():
    """Test directory loader functionality."""
    # Create test directory
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Create test files
    (test_dir / "doc1.txt").write_text("Test content 1")
    (test_dir / "doc2.md").write_text("# Test content 2")
    
    # Initialize RAG
    rag = HawkinsRAG()
    
    # Test loading
    result = rag.load_document(str(test_dir), source_type="directory")
    
    # Verify results
    assert result["meta_data"]["file_count"] == 2
    assert "Test content" in result["content"]
```

## Related Documentation
- [Text Loader](./text_loader.md)
- [PDF Loader](./pdf_loader.md)
- [Configuration Guide](../configuration.md)
