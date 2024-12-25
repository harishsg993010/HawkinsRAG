"""CSV file loader implementation."""
import csv
import hashlib
from typing import Any, Dict, Optional
from pathlib import Path
import logging
from io import StringIO
import requests
from urllib.parse import urlparse
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class CSVLoader(BaseLoader):
    """Loader for CSV files and URLs."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize CSV loader with optional configuration."""
        super().__init__(config)
        self.config = config or {}
        self.delimiter = self.config.get('delimiter', ',')

    def _detect_delimiter(self, sample: str) -> str:
        """Detect the delimiter used in the CSV content."""
        if self.delimiter:
            return self.delimiter

        common_delimiters = [',', ';', '\t', '|']
        counts = {d: sample.count(d) for d in common_delimiters}
        return max(counts.items(), key=lambda x: x[1])[0]

    def load(self, source: str) -> Dict[str, Any]:
        """Load and process CSV data from file or URL.

        Args:
            source: Path to CSV file or URL

        Returns:
            Dict containing:
                - content: Processed CSV content as text
                - meta_data: Dictionary of metadata about the content
        """
        csv_content = None
        try:
            # Determine if source is URL or file
            url = urlparse(source)
            if all([url.scheme, url.netloc]):
                if url.scheme not in ['http', 'https']:
                    raise ValueError("Only HTTP(S) URLs are supported")
                response = requests.get(source)
                response.raise_for_status()
                csv_content = StringIO(response.text)
                metadata = {
                    "source_type": "url",
                    "url": source
                }
            else:
                path = Path(source)
                if not path.exists():
                    raise ValueError(f"CSV file not found: {source}")
                csv_content = open(path, 'r', encoding='utf-8')
                metadata = {
                    "source_type": "file",
                    "file_path": str(path),
                    "file_size": path.stat().st_size
                }

            # Read first line to detect delimiter
            first_line = csv_content.readline()
            csv_content.seek(0)
            delimiter = self._detect_delimiter(first_line)

            # Process CSV content
            reader = csv.DictReader(csv_content, delimiter=delimiter)
            headers = reader.fieldnames if reader.fieldnames else []
            content_lines = []

            for row in reader:
                line = " | ".join([f"{k}: {v}" for k, v in row.items() if v])
                if line:  # Only append non-empty lines
                    content_lines.append(line)

            # Create content string
            content = f"Headers: {', '.join(headers)}\n\n"
            content += "\n".join(content_lines)

            # Generate document ID
            doc_id = hashlib.sha256(content.encode()).hexdigest()[:16]

            logger.info(f"Successfully loaded CSV from {source}")
            return {
                "content": content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": source,
                    "type": "csv",
                    "headers": headers,
                    "total_rows": len(content_lines),
                    **metadata
                }
            }

        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise ValueError(f"Error loading CSV: {str(e)}")

        finally:
            if csv_content:
                csv_content.close()