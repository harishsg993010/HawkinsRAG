from typing import List, Dict, Any

def chunk_text(text: str, source_name: str, chunk_size: int) -> List[Dict[str, Any]]:
    """Split text into chunks with metadata."""
    words = text.split()
    chunks = []
    current_chunk = []
    chunk_number = 1

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= chunk_size:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "name": f"{source_name}_chunk_{chunk_number}",
                "column": "Semantic",
                "properties": {
                    "content": chunk_text,
                    "source": source_name,
                    "chunk_number": chunk_number,
                },
                "relationships": {
                    "part_of": [source_name],
                    "next_chunk": (
                        [f"{source_name}_chunk_{chunk_number + 1}"]
                        if len(words) > chunk_size
                        else []
                    )
                }
            })
            current_chunk = []
            chunk_number += 1

    # Handle remaining text
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunks.append({
            "name": f"{source_name}_chunk_{chunk_number}",
            "column": "Semantic",
            "properties": {
                "content": chunk_text,
                "source": source_name,
                "chunk_number": chunk_number,
            },
            "relationships": {
                "part_of": [source_name]
            }
        })

    return chunks

def is_readable(text: str) -> bool:
    """Check if text is readable (contains valid characters)."""
    if not text:
        return False

    # Count valid characters (letters, numbers, punctuation)
    valid_chars = sum(1 for c in text if c.isalnum() or c.isspace() or c in '.,!?-:;()[]{}')
    total_chars = len(text)

    # Text is readable if at least 80% of characters are valid
    return valid_chars / total_chars >= 0.8 if total_chars > 0 else False