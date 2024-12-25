# HawkinsRAG Configuration Guide

## Basic Configuration

HawkinsRAG can be configured through a dictionary passed to the constructor:

```python
config = {
    "storage_type": "sqlite",  # or "postgres"
    "db_path": "hawkins_rag.db",
    "chunk_size": 500,
    "openai_api_key": "your-api-key",  # Optional, for embeddings
    "loader_config": {
        # Loader-specific configurations
    }
}

rag = HawkinsRAG(config=config)
```

## Storage Configuration

### SQLite Storage
```python
config = {
    "storage_type": "sqlite",
    "db_path": "hawkins_rag.db"
}
```

### PostgreSQL Storage
```python
config = {
    "storage_type": "postgres",
    "db_url": "postgresql://user:pass@localhost:5432/dbname"
}
```

## Loader Configurations

### YouTube Loader
```python
config = {
    "loader_config": {
        "youtube": {
            "api_key": "YOUR_YOUTUBE_API_KEY"
        }
    }
}
```

### GitHub Loader
```python
config = {
    "loader_config": {
        "github": {
            "token": "YOUR_GITHUB_TOKEN"
        }
    }
}
```

### Gmail Loader
```python
config = {
    "loader_config": {
        "gmail": {
            "token_path": "gmail_token.pickle"
        }
    }
}
```

### Directory Loader
```python
config = {
    "loader_config": {
        "directory": {
            "recursive": True,
            "extensions": ["txt", "pdf", "docx", "md"]
        }
    }
}
```

## Content Processing Configuration

### Chunk Size
```python
config = {
    "chunk_size": 500  # Number of tokens per chunk
}
```

### Embedding Configuration
```python
config = {
    "embedding": {
        "model": "text-embedding-ada-002",
        "batch_size": 100
    }
}
```

## Environment Variables

Required environment variables for different loaders:

```bash
# Core functionality
OPENAI_API_KEY=your-openai-key

# YouTube loader
YOUTUBE_API_KEY=your-youtube-key

# GitHub loader
GITHUB_TOKEN=your-github-token

# Google services
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

## Advanced Configuration

### Error Handling
```python
config = {
    "error_handling": {
        "max_retries": 3,
        "retry_delay": 1.0,
        "ignore_errors": False
    }
}
```

### Logging Configuration
```python
config = {
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}
```

## Best Practices

1. **Security**
   - Store sensitive keys in environment variables
   - Use appropriate access tokens
   - Implement proper error handling

2. **Performance**
   - Adjust chunk size based on content type
   - Configure batch processing for large datasets
   - Use appropriate storage backend

3. **Maintenance**
   - Regular token rotation
   - Monitoring and logging
   - Regular backups

## Example Complete Configuration

```python
config = {
    "storage_type": "postgres",
    "db_url": "postgresql://user:pass@localhost:5432/dbname",
    "chunk_size": 500,
    "loader_config": {
        "youtube": {
            "api_key": os.getenv("YOUTUBE_API_KEY")
        },
        "github": {
            "token": os.getenv("GITHUB_TOKEN")
        },
        "directory": {
            "recursive": True,
            "extensions": ["txt", "pdf", "docx"]
        }
    },
    "embedding": {
        "model": "text-embedding-ada-002",
        "batch_size": 100
    },
    "error_handling": {
        "max_retries": 3,
        "retry_delay": 1.0
    },
    "logging": {
        "level": "INFO"
    }
}

rag = HawkinsRAG(config=config)
```
