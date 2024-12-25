import os
import hashlib
from typing import Any, Dict, Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
from ..utils.loader_registry import BaseLoader

class PostgreSQLLoader(BaseLoader):
    """Loader for PostgreSQL databases."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize PostgreSQL loader with configuration."""
        if not config:
            # Try to get configuration from environment variables
            config = {
                "host": os.getenv("PGHOST", "localhost"),
                "port": os.getenv("PGPORT", "5432"),
                "database": os.getenv("PGDATABASE"),
                "user": os.getenv("PGUSER"),
                "password": os.getenv("PGPASSWORD")
            }

        if not all([config.get("database"), config.get("user"), config.get("password")]):
            raise ValueError(
                "PostgreSQL loader requires database credentials. "
                "Set them in config or environment variables."
            )

        self.config = config

    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["database"],
            user=self.config["user"],
            password=self.config["password"],
            cursor_factory=RealDictCursor
        )

    def load(self, source: str) -> Any:
        """Load content from PostgreSQL query.

        Args:
            source: SQL query to execute

        Returns:
            Dict containing document ID and query results
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(source)
                    results = cur.fetchall()

                    if not results:
                        raise ValueError("Query returned no results")

                    # Convert results to list of dicts
                    data = []
                    for row in results:
                        content = "\n".join(f"{k}: {v}" for k, v in dict(row).items())
                        data.append({
                            "content": content,
                            "meta_data": {
                                "query": source,
                                "database": self.config["database"],
                                "row_count": len(results)
                            }
                        })

                    # Generate document ID
                    doc_id = hashlib.sha256(
                        (source + str(data)).encode()
                    ).hexdigest()

                    return {
                        "doc_id": doc_id,
                        "data": data
                    }

        except Exception as e:
            raise ValueError(f"Error executing PostgreSQL query: {str(e)}")