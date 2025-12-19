"""
Recreate Qdrant Collection for Gemini Embeddings (768 dimensions)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from app.core.config import settings

def main():
    print("=" * 60)
    print("Recreating Qdrant Collection for Gemini (768 dimensions)")
    print("=" * 60)

    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key
    )

    # Delete existing collection
    try:
        print(f"\nDeleting existing collection '{settings.qdrant_collection_name}'...")
        client.delete_collection(settings.qdrant_collection_name)
        print("Collection deleted")
    except Exception as e:
        print(f"Note: {e}")

    # Create new collection with 768 dimensions for Gemini
    print(f"\nCreating new collection with 768 dimensions...")
    client.create_collection(
        collection_name=settings.qdrant_collection_name,
        vectors_config=VectorParams(
            size=768,  # Gemini text-embedding-004 dimension
            distance=Distance.COSINE
        )
    )

    print("Collection created successfully!")
    print("\nNext step: Run ingestion to populate the collection")
    print("  python scripts/run_ingestion.py")

if __name__ == "__main__":
    main()
