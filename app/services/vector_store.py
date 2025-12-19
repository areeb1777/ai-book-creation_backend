"""
Vector Store Service - Qdrant Client

Handles vector storage and similarity search operations.
Provides high-level interface for document chunk operations.
"""

from typing import List, Dict, Any, Optional
from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Client for Qdrant vector database operations"""

    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection_name

    def upsert_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> int:
        """
        Insert or update document chunks with embeddings

        Args:
            chunks: List of chunk metadata dictionaries
            embeddings: List of embedding vectors (1536 dimensions)

        Returns:
            Number of chunks upserted
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        try:
            points = []
            for chunk, embedding in zip(chunks, embeddings):
                point = PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk["text"],
                        "chapter": chunk.get("chapter", ""),
                        "section": chunk.get("section", ""),
                        "source_file": chunk["source_file"],
                        "heading_path": chunk.get("heading_path", []),
                        "page_number": chunk.get("page_number"),
                        "chunk_index": chunk["chunk_index"],
                        "created_at": chunk.get("created_at", "")
                    }
                )
                points.append(point)

            # Upsert in batches of 100
            batch_size = 100
            total_upserted = 0

            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                total_upserted += len(batch)
                logger.info(f"Upserted batch: {len(batch)} points (total: {total_upserted}/{len(points)})")

            logger.info(f"✅ Successfully upserted {total_upserted} chunks")
            return total_upserted

        except Exception as e:
            logger.error(f"Failed to upsert chunks: {e}")
            raise

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.7,
        filter_chapter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity

        Args:
            query_embedding: Query vector (1536 dimensions)
            top_k: Number of results to return
            score_threshold: Minimum similarity score (0-1)
            filter_chapter: Optional filter by chapter

        Returns:
            List of matching chunks with metadata and scores
        """
        try:
            # Build filter if chapter specified
            query_filter = None
            if filter_chapter:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="chapter",
                            match=MatchValue(value=filter_chapter)
                        )
                    ]
                )

            # Perform search (updated for Qdrant client 1.16+)
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=query_filter
            ).points

            # Format results
            chunks = []
            for result in results:
                chunk = {
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload["text"],
                    "chapter": result.payload.get("chapter", ""),
                    "section": result.payload.get("section", ""),
                    "source_file": result.payload["source_file"],
                    "heading_path": result.payload.get("heading_path", []),
                    "page_number": result.payload.get("page_number"),
                    "chunk_index": result.payload["chunk_index"]
                }
                chunks.append(chunk)

            logger.info(f"Found {len(chunks)} chunks (threshold: {score_threshold})")
            return chunks

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def delete_collection(self):
        """Delete entire collection (use with caution!)"""
        try:
            self.client.delete_collection(self.collection_name)
            logger.warning(f"Collection '{self.collection_name}' deleted")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.name,
                "points_count": info.points_count,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            raise

    def test_connection(self) -> bool:
        """Test Qdrant connection"""
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            if self.collection_name in collection_names:
                logger.info(f"✅ Collection '{self.collection_name}' exists")
                return True
            else:
                logger.warning(f"⚠️ Collection '{self.collection_name}' not found")
                return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Global client instance
vector_store = VectorStore()
