"""
RAG Query Pipeline

Orchestrates the full RAG workflow:
1. Input validation and sanitization
2. Query embedding generation
3. Vector similarity search
4. Answer generation with context
5. Source citation extraction
6. Query logging
"""

import time
import re
from typing import List, Dict, Any, Optional
from uuid import UUID
from app.services.embeddings import embeddings_service
from app.services.vector_store import vector_store
from app.services.answer_generator import answer_generator
from app.services.metadata_store import neon_client
from app.api.models.request import QueryRequest, ConversationTurn
from app.api.models.response import QueryResponse, SourceCitation
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """RAG query pipeline orchestrator"""

    def __init__(self):
        pass

    def process_query(self, request: QueryRequest) -> QueryResponse:
        """
        Process full-book query through RAG pipeline

        Args:
            request: Query request with question and context

        Returns:
            Query response with answer and sources
        """
        start_time = time.time()

        try:
            # Step 1: Validate and sanitize input
            sanitized_query = self._sanitize_input(request.query)
            logger.info(f"Processing query: '{sanitized_query[:100]}...'")

            # Step 2: Generate query embedding
            logger.info("Generating query embedding...")
            query_embedding = embeddings_service.generate_embedding(sanitized_query)

            # Step 3: Retrieve top-k chunks from Qdrant
            logger.info(f"Searching for top-{request.top_k} relevant chunks...")
            chunks = vector_store.search(
                query_embedding=query_embedding,
                top_k=request.top_k,
                score_threshold=settings.similarity_threshold
            )

            if not chunks:
                logger.warning("No relevant chunks found (all below threshold)")
                return self._no_information_response(request.session_id, start_time)

            logger.info(f"Found {len(chunks)} relevant chunks")

            # Step 4: Generate answer
            logger.info("Generating answer...")
            answer_text = answer_generator.generate_answer(
                query=sanitized_query,
                context_chunks=chunks,
                conversation_history=request.conversation_history
            )

            # Step 5: Extract source citations
            sources = self._extract_sources(chunks)

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Step 6: Log query and answer
            neon_client.log_query(
                session_id=request.session_id,
                query_text=sanitized_query,
                query_mode="full_book",
                answer_text=answer_text,
                source_chunks=[s.model_dump() for s in sources],
                response_time_ms=response_time_ms
            )

            # Step 7: Return response
            return QueryResponse(
                answer=answer_text,
                sources=sources,
                mode=request.query_mode,
                session_id=request.session_id,
                response_time_ms=response_time_ms
            )

        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise

    def _sanitize_input(self, text: str) -> str:
        """
        Sanitize user input to prevent injection attacks

        Args:
            text: Raw user input

        Returns:
            Sanitized text
        """
        # Remove potential SQL injection patterns
        sanitized = re.sub(r"[';\"\\]", "", text)

        # Remove potential XSS patterns
        sanitized = re.sub(r"<script.*?>.*?</script>", "", sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r"<.*?>", "", sanitized)

        # Trim whitespace
        sanitized = sanitized.strip()

        return sanitized

    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[SourceCitation]:
        """
        Extract source citations from chunks

        Args:
            chunks: Retrieved chunks with metadata

        Returns:
            List of source citations
        """
        sources = []

        for chunk in chunks:
            # Generate URL from source file
            # Convert "chapter-1-spec-kit.md" to "/docs/chapter-1-spec-kit"
            file = chunk["source_file"]
            base_url = f"/docs/{file.replace('.md', '')}"

            # Add section anchor if available
            section = chunk.get("section", "")
            if section:
                # Convert "Introduction to Spec-Kit Plus" to "#introduction-to-spec-kit-plus"
                section_slug = section.lower().replace(" ", "-").replace("'", "")
                url = f"{base_url}#{section_slug}"
            else:
                url = base_url

            # Create citation
            citation = SourceCitation(
                chapter=chunk.get("chapter", "Unknown"),
                section=chunk.get("section"),
                file=file,
                url=url,
                similarity_score=chunk["score"],
                excerpt=chunk["text"][:200] if len(chunk["text"]) > 200 else chunk["text"]
            )

            sources.append(citation)

        return sources

    def _no_information_response(self, session_id: UUID, start_time: float) -> QueryResponse:
        """
        Generate response when no relevant information found

        Args:
            session_id: Session UUID
            start_time: Query start time

        Returns:
            QueryResponse with "no information" message
        """
        response_time_ms = int((time.time() - start_time) * 1000)

        return QueryResponse(
            answer="I couldn't find information about that in this book.",
            sources=[],
            mode="full_book",
            session_id=session_id,
            response_time_ms=response_time_ms
        )


# Global pipeline instance
rag_pipeline = RAGPipeline()
