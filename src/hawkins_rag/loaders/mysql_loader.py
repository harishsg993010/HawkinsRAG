import os
import hashlib
from typing import Any, Dict, Optional
import mysql.connector
from .base import BaseLoader

class MySQLLoader(BaseLoader):
    """Loader for MySQL databases."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize MySQL loader with configuration."""
        if not config:
            # Try to get configuration from environment variables
            config = {
                "host": os.getenv("MYSQL_HOST", "localhost"),
                "port": int(os.getenv("MYSQL_PORT", "3306")),
                "database": os.getenv("MYSQL_DATABASE"),
                "user": os.getenv("MYSQL_USER"),
                "password": os.getenv("MYSQL_PASSWORD")
            }

        if not all([config.get("database"), config.get("user"), config.get("password")]):
            raise ValueError(
                "MySQL loader requires database credentials. "
                "Set them in config or environment variables."
            )

        self.config = config

    def _get_connection(self):
        """Get database connection."""
        try:
            return mysql.connector.connect(
                host=self.config["host"],
                port=self.config["port"],
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"]
            )
        except mysql.connector.Error as e:
            raise ValueError(f"Failed to connect to MySQL: {str(e)}")

    def load(self, source: str) -> Any:
        """Load content from MySQL query.

        Args:
            source: SQL query to execute

        Returns:
            Dict containing document ID and query results
        """
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(source)
            results = cursor.fetchall()

            if not results:
                raise ValueError("Query returned no results")

            # Convert results to list of dicts
            data = []
            for row in results:
                content = "\n".join(f"{k}: {v}" for k, v in row.items())
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
            raise ValueError(f"Error executing MySQL query: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()