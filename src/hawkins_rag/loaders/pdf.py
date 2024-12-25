"""PDF document loader implementation."""
import hashlib
from typing import Any, Dict
from pathlib import Path
import PyPDF2
import logging
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class PDFLoader(BaseLoader):
    """Loader for PDF files."""

    def load(self, source: str) -> Dict[str, Any]:
        """Load text content from a PDF file.

        Args:
            source: Path to the PDF file

        Returns:
            Dict containing document content and metadata
        """
        try:
            path = Path(source)
            if not path.exists():
                raise ValueError(f"PDF file not found: {source}")

            # Extract text from PDF
            text_content = ""
            metadata = {}

            with open(path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = {
                    "total_pages": len(pdf_reader.pages),
                    "file_name": path.name,
                    "file_size": path.stat().st_size
                }

                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    if text.strip():
                        text_content += f"\n\n=== Page {page_num} ===\n\n"
                        text_content += text

            # Generate document ID
            doc_id = hashlib.sha256(str(path).encode()).hexdigest()[:16]

            logger.info(f"Successfully loaded PDF: {path.name}")
            return {
                "content": text_content.strip(),
                "meta_data": {
                    "doc_id": doc_id,
                    "source": str(path),
                    "type": "pdf",
                    **metadata
                }
            }

        except Exception as e:
            logger.error(f"Error loading PDF: {str(e)}")
            raise ValueError(f"Error loading PDF: {str(e)}")