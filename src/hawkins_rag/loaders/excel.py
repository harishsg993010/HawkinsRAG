"""Excel file loader implementation."""
import hashlib
from typing import Any, Dict, Optional
from pathlib import Path
import pandas as pd
import logging
from ..utils.base import BaseLoader

logger = logging.getLogger(__name__)

class ExcelLoader(BaseLoader):
    """Loader for Excel files (.xls and .xlsx)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Excel loader with optional configuration."""
        super().__init__(config)

    def load(self, source: str) -> Dict[str, Any]:
        """Load and process Excel file content.

        Args:
            source: Path to Excel file

        Returns:
            Dict containing:
                - content: Processed Excel content as text
                - meta_data: Dictionary of metadata about the content
        """
        try:
            path = Path(source)
            if not path.exists():
                raise ValueError(f"Excel file not found: {source}")

            # Read all sheets
            excel_file = pd.ExcelFile(str(path))
            content_parts = []
            sheet_info = []

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                sheet_info.append({
                    "name": sheet_name,
                    "rows": len(df),
                    "columns": list(df.columns)
                })

                # Add sheet header
                content_parts.append(f"\n=== Sheet: {sheet_name} ===\n")

                # Add column names
                content_parts.append("Columns: " + ", ".join(df.columns))

                # Convert each row to text
                for idx, row in df.iterrows():
                    row_text = " | ".join([f"{col}: {value}" for col, value in row.items() if pd.notna(value)])
                    content_parts.append(row_text)

            # Join all content
            content = "\n".join(content_parts)

            # Generate document ID
            doc_id = hashlib.sha256(
                (str(path) + content[:100]).encode()
            ).hexdigest()[:16]

            logger.info(f"Successfully loaded Excel file: {path.name}")
            return {
                "content": content,
                "meta_data": {
                    "doc_id": doc_id,
                    "source": str(path),
                    "type": "excel",
                    "file_name": path.name,
                    "file_size": path.stat().st_size,
                    "sheets": sheet_info,
                    "total_sheets": len(sheet_info)
                }
            }

        except Exception as e:
            logger.error(f"Error loading Excel file: {str(e)}")
            raise ValueError(f"Error loading Excel file: {str(e)}")