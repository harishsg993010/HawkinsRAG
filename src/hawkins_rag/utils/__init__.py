"""Utility functions for the hawkins_rag package."""
from typing import List, Dict, Any, Union
from pathlib import Path

def is_readable(path: Union[str, Path]) -> bool:
    """Check if a file exists and is readable.

    Args:
        path: Path to the file to check

    Returns:
        bool: True if file exists and is readable
    """
    try:
        path = Path(path)
        return path.exists() and os.access(path, os.R_OK)
    except Exception:
        return False

def chunk_text(content: Union[str, Dict], source_name: str, chunk_size: int = 1000) -> List[Dict[str, Any]]:
    """Split content into chunks for processing.

    Args:
        content: Text content or dictionary containing content and metadata
        source_name: Name of the source document
        chunk_size: Maximum size of each chunk in characters

    Returns:
        List of chunks with metadata
    """
    chunks = []
    chunk_counter = 0

    # Handle both string content and dictionary with content/metadata
    if isinstance(content, dict):
        text = content.get("content", "")
        metadata = content.get("meta_data", {})
    else:
        text = str(content)
        metadata = {}

    # Split content into paragraphs
    paragraphs = text.split("\n\n")
    current_chunk = []
    current_size = 0

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        # If adding this paragraph would exceed chunk size, save current chunk
        if current_size + len(paragraph) > chunk_size and current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append({
                "name": f"{source_name}_chunk_{chunk_counter}",
                "column": "Semantic",
                "properties": {
                    "content": chunk_text,
                    **metadata,
                    "chunk_index": chunk_counter,
                    "source_name": source_name
                }
            })
            chunk_counter += 1
            current_chunk = []
            current_size = 0

        current_chunk.append(paragraph)
        current_size += len(paragraph)

    # Don't forget the last chunk
    if current_chunk:
        chunk_text = "\n\n".join(current_chunk)
        chunks.append({
            "name": f"{source_name}_chunk_{chunk_counter}",
            "column": "Semantic",
            "properties": {
                "content": chunk_text,
                **metadata,
                "chunk_index": chunk_counter,
                "source_name": source_name
            }
        })

    return chunks

import os