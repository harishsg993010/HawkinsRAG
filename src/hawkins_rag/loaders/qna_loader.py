"""QnA loader implementation for processing question-answer pairs."""
import hashlib
import json
from typing import Any, Dict, List, Optional
from pathlib import Path
import logging
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class QnALoader(BaseLoader):
    """Loader for Question-Answer pair files in JSON or text format."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize QnA loader with optional configuration."""
        super().__init__(config)
        self.config = config or {}

    def _process_json_qna(self, content: str) -> List[Dict[str, str]]:
        """Process JSON format QnA pairs."""
        try:
            data = json.loads(content)
            if not isinstance(data, list):
                raise ValueError("JSON content must be an array of QnA pairs")

            processed_pairs = []
            for i, pair in enumerate(data, 1):
                if not isinstance(pair, dict):
                    raise ValueError(f"Invalid pair format at index {i}")

                # Validate required fields
                question = pair.get('question')
                answer = pair.get('answer')

                if not question or not answer:
                    raise ValueError(f"Missing question or answer at index {i}")

                processed_pairs.append({
                    'question': question.strip(),
                    'answer': answer.strip(),
                    'index': i
                })

            return processed_pairs
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")

    def _process_text_qna(self, content: str) -> List[Dict[str, str]]:
        """Process text format QnA pairs."""
        lines = content.strip().split('\n')
        processed_pairs = []
        current_q = None
        current_a = []
        pair_index = 1

        for line in lines:
            line = line.strip()
            if not line:
                if current_q and current_a:
                    processed_pairs.append({
                        'question': current_q,
                        'answer': ' '.join(current_a),
                        'index': pair_index
                    })
                    pair_index += 1
                    current_q = None
                    current_a = []
            elif line.startswith('Q:'):
                if current_q and current_a:
                    processed_pairs.append({
                        'question': current_q,
                        'answer': ' '.join(current_a),
                        'index': pair_index
                    })
                    pair_index += 1
                current_q = line[2:].strip()
                current_a = []
            elif line.startswith('A:'):
                if not current_q:
                    raise ValueError("Found answer without a question")
                current_a.append(line[2:].strip())
            elif current_a:
                current_a.append(line)
            else:
                raise ValueError("Invalid format: lines must start with Q: or A:")

        # Add the last pair if exists
        if current_q and current_a:
            processed_pairs.append({
                'question': current_q,
                'answer': ' '.join(current_a),
                'index': pair_index
            })

        return processed_pairs

    def load(self, source: str) -> Dict[str, Any]:
        """Load and process QnA pairs from a file.

        Args:
            source: Path to the QnA file (JSON or text format)

        Returns:
            Dict containing:
                - content: Combined QnA content
                - meta_data: File metadata and statistics
        """
        try:
            path = Path(source)
            if not path.exists():
                raise ValueError(f"QnA file not found: {source}")

            logger.info(f"Loading QnA file: {source}")

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Process based on file format
            if path.suffix.lower() == '.json':
                qna_pairs = self._process_json_qna(content)
            else:
                qna_pairs = self._process_text_qna(content)

            if not qna_pairs:
                raise ValueError("No valid QnA pairs found")

            # Format content for RAG system with clear section breaks
            formatted_content = "\n\n=== QnA Pair {} ===\n".join(
                f"Question: {pair['question']}\nAnswer: {pair['answer']}"
                for pair in qna_pairs
            ).format(*range(1, len(qna_pairs) + 1))

            # Generate document ID
            doc_id = hashlib.sha256(
                (str(path) + formatted_content[:100]).encode()
            ).hexdigest()[:16]

            logger.info(f"Successfully loaded {len(qna_pairs)} QnA pairs from {source}")

            return {
                "content": formatted_content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": str(path),
                    "type": "qna",
                    "format": "json" if path.suffix.lower() == '.json' else "text",
                    "pair_count": len(qna_pairs),
                    "pairs": [
                        {
                            "index": pair['index'],
                            "question": pair['question']
                        }
                        for pair in qna_pairs
                    ]
                }
            }

        except Exception as e:
            logger.error(f"Error loading QnA file: {str(e)}")
            raise ValueError(f"QnA loader failed: {str(e)}")

# For backward compatibility and explicit exports
__all__ = ['QnALoader']