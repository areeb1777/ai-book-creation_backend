"""
Qdrant Cloud Setup Script

Creates the vector collection for storing document embeddings.
Run this script once to initialize the Qdrant collection.

Usage:
    python scripts/setup_qdrant.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def create_collection():
    """Create Qdrant collection for document chunks"""
    logger.info("Starting Qdrant collection setup...")

    try:
        # Initialize Qdrant client
        logger.info(f"Connecting to Qdrant at {settings.qdrant_url}...")
        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

        # Check if collection already exists
        collections = client.get_collections().collections
        existing_names = [c.name for c in collections]

        if settings.qdrant_collection_name in existing_names:
            logger.warning(f"Collection '{settings.qdrant_collection_name}' already exists")

            # Optionally recreate
            response = input("Delete and recreate collection? (yes/no): ")
            if response.lower() == 'yes':
                logger.info("Deleting existing collection...")
                client.delete_collection(settings.qdrant_collection_name)
            else:
                logger.info("Keeping existing collection")
                return True

        # Create collection
        logger.info(f"Creating collection '{settings.qdrant_collection_name}'...")
        client.create_collection(
            collection_name=settings.qdrant_collection_name,
            vectors_config=VectorParams(
                size=1536,  # OpenAI text-embedding-3-small dimension
                distance=Distance.COSINE
            )
        )

        # Verify collection created
        collection_info = client.get_collection(settings.qdrant_collection_name)
        logger.info(f"Collection created successfully:")
        logger.info(f"  - Name: {collection_info.name}")
        logger.info(f"  - Vector size: {collection_info.config.params.vectors.size}")
        logger.info(f"  - Distance: {collection_info.config.params.vectors.distance}")
        logger.info(f"  - Points count: {collection_info.points_count}")

        logger.info("✅ Qdrant collection setup completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Qdrant setup error: {e}")
        return False


def verify_connection():
    """Verify Qdrant connection"""
    try:
        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        collections = client.get_collections()
        logger.info(f"✅ Qdrant connection verified. Collections: {[c.name for c in collections.collections]}")
        return True
    except Exception as e:
        logger.error(f"❌ Qdrant connection failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Qdrant Cloud Setup")
    print("=" * 60)

    # Verify connection first
    if not verify_connection():
        print("\n❌ Failed to connect to Qdrant. Check QDRANT_URL and QDRANT_API_KEY in .env")
        sys.exit(1)

    # Create collection
    if create_collection():
        print("\n✅ Setup completed successfully!")
        print(f"\nCollection '{settings.qdrant_collection_name}' is ready for ingestion.")
        print("\nNext steps:")
        print("1. Run scripts/run_ingestion.py to populate with book content")
        print("2. Test health endpoint: GET http://localhost:8000/api/health")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Check logs above for details.")
        sys.exit(1)
