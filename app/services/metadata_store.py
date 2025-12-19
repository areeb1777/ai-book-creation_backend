"""
Metadata Store Service - Neon Postgres Client

Handles query logging and ingestion tracking in Neon Serverless Postgres.
Provides async database operations for high performance.
"""

import psycopg2
import json
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class NeonClient:
    """Client for Neon Serverless Postgres operations"""

    def __init__(self):
        self.database_url = settings.database_url
        self._connection = None

    def get_connection(self):
        """Get database connection (creates new if needed)"""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(self.database_url)
        return self._connection

    def close(self):
        """Close database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()

    def log_query(
        self,
        session_id: UUID,
        query_text: str,
        query_mode: str,
        answer_text: str,
        source_chunks: List[Dict[str, Any]],
        response_time_ms: int,
        selected_text: Optional[str] = None
    ) -> UUID:
        """
        Log a query and its response to database

        Args:
            session_id: Session UUID
            query_text: User's question
            query_mode: 'full_book' or 'selected_text'
            answer_text: Generated answer
            source_chunks: List of source citations
            response_time_ms: Processing time in milliseconds
            selected_text: Optional selected text (for selected_text mode)

        Returns:
            UUID of created log entry
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Convert source_chunks to JSONB
            source_chunks_json = json.dumps(source_chunks)

            cursor.execute("""
                INSERT INTO query_logs (
                    session_id, query_text, query_mode, selected_text,
                    answer_text, source_chunks, response_time_ms
                )
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s)
                RETURNING id
            """, (
                str(session_id),
                query_text,
                query_mode,
                selected_text,
                answer_text,
                source_chunks_json,
                response_time_ms
            ))

            log_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()

            logger.info(f"Query logged: {log_id}")
            return UUID(log_id)

        except Exception as e:
            logger.error(f"Failed to log query: {e}")
            if conn:
                conn.rollback()
            raise

    def start_ingestion_log(
        self,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """
        Start ingestion log entry

        Args:
            metadata: Optional metadata about ingestion parameters

        Returns:
            UUID of created log entry
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            metadata_json = json.dumps(metadata) if metadata else None

            cursor.execute("""
                INSERT INTO ingestion_logs (status, metadata)
                VALUES ('running', %s::jsonb)
                RETURNING id
            """, (metadata_json,))

            log_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()

            logger.info(f"Ingestion started: {log_id}")
            return UUID(log_id)

        except Exception as e:
            logger.error(f"Failed to start ingestion log: {e}")
            if conn:
                conn.rollback()
            raise

    def complete_ingestion_log(
        self,
        log_id: UUID,
        total_chunks: int,
        total_files: int,
        error_message: Optional[str] = None
    ):
        """
        Complete ingestion log entry

        Args:
            log_id: Log entry UUID
            total_chunks: Number of chunks created
            total_files: Number of files processed
            error_message: Optional error message if failed
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            status = 'failed' if error_message else 'completed'

            cursor.execute("""
                UPDATE ingestion_logs
                SET completed_at = NOW(),
                    status = %s,
                    total_chunks = %s,
                    total_files = %s,
                    error_message = %s
                WHERE id = %s
            """, (status, total_chunks, total_files, error_message, str(log_id)))

            conn.commit()
            cursor.close()

            logger.info(f"Ingestion completed: {log_id} ({status})")

        except Exception as e:
            logger.error(f"Failed to complete ingestion log: {e}")
            if conn:
                conn.rollback()
            raise

    def get_query_logs(
        self,
        session_id: Optional[UUID] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve query logs

        Args:
            session_id: Optional filter by session
            limit: Maximum number of logs to return

        Returns:
            List of query log dictionaries
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if session_id:
                cursor.execute("""
                    SELECT id, session_id, query_text, query_mode, answer_text,
                           source_chunks, response_time_ms, created_at
                    FROM query_logs
                    WHERE session_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (str(session_id), limit))
            else:
                cursor.execute("""
                    SELECT id, session_id, query_text, query_mode, answer_text,
                           source_chunks, response_time_ms, created_at
                    FROM query_logs
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (limit,))

            rows = cursor.fetchall()
            cursor.close()

            logs = []
            for row in rows:
                logs.append({
                    "id": row[0],
                    "session_id": row[1],
                    "query_text": row[2],
                    "query_mode": row[3],
                    "answer_text": row[4],
                    "source_chunks": row[5],  # Already parsed as dict
                    "response_time_ms": row[6],
                    "created_at": row[7].isoformat()
                })

            return logs

        except Exception as e:
            logger.error(f"Failed to retrieve query logs: {e}")
            raise

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            return result[0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Global client instance
neon_client = NeonClient()
