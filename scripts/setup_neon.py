"""
Neon Serverless Postgres Setup Script

Initializes the database schema and verifies connection.
Run this script once to set up the database tables.

Usage:
    python scripts/setup_neon.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from psycopg2 import sql
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def read_schema_file() -> str:
    """Read SQL schema file"""
    schema_path = Path(__file__).parent.parent / "app" / "core" / "database_schema.sql"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, 'r') as f:
        return f.read()


def setup_database():
    """Initialize Neon database with schema"""
    logger.info("Starting Neon database setup...")

    try:
        # Connect to database
        logger.info(f"Connecting to Neon database...")
        conn = psycopg2.connect(settings.database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        # Read schema SQL
        schema_sql = read_schema_file()

        # Execute schema
        logger.info("Executing schema SQL...")
        cursor.execute(schema_sql)

        # Verify tables created
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)

        tables = cursor.fetchall()
        logger.info(f"Created tables: {[t[0] for t in tables]}")

        # Test insert/query on query_logs
        logger.info("Testing query_logs table...")
        cursor.execute("""
            INSERT INTO query_logs (session_id, query_text, query_mode, answer_text, response_time_ms)
            VALUES (gen_random_uuid(), 'Test query', 'full_book', 'Test answer', 100)
            RETURNING id
        """)
        test_id = cursor.fetchone()[0]
        logger.info(f"Test record created: {test_id}")

        # Clean up test record
        cursor.execute("DELETE FROM query_logs WHERE id = %s", (test_id,))
        logger.info("Test record deleted")

        # Close connection
        cursor.close()
        conn.close()

        logger.info("✅ Neon database setup completed successfully!")
        return True

    except psycopg2.Error as e:
        logger.error(f"❌ Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False


def verify_connection():
    """Verify database connection"""
    try:
        conn = psycopg2.connect(settings.database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        logger.info(f"✅ Database connection verified: {version}")
        return True
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Neon Serverless Postgres Setup")
    print("=" * 60)

    # Verify connection first
    if not verify_connection():
        print("\n❌ Failed to connect to database. Check DATABASE_URL in .env")
        sys.exit(1)

    # Setup database schema
    if setup_database():
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run scripts/setup_qdrant.py to initialize Qdrant collection")
        print("2. Test health endpoint: GET http://localhost:8000/api/health")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Check logs above for details.")
        sys.exit(1)
