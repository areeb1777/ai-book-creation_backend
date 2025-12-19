"""
Query Endpoint

POST /api/query - Full-book question answering using RAG pipeline.
"""

from fastapi import APIRouter, HTTPException, status
from app.api.models.request import QueryRequest
from app.api.models.response import QueryResponse, ErrorResponse, SourceCitation
from app.services.query_pipeline import rag_pipeline
from app.services.demo_mode import demo_service
from app.core.config import settings
from app.core.logging import get_logger
import uuid

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/api/query",
    response_model=QueryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    },
    summary="Query full book",
    description="Answer question using full book corpus via vector similarity search"
)
async def query_full_book(request: QueryRequest):
    """
    Query the full book corpus

    Retrieves relevant content chunks using vector similarity search,
    then generates an answer grounded in retrieved context only.

    Request Body:
        - query: User's natural language question (10-2000 chars)
        - conversation_history: Optional previous turns for context
        - session_id: Optional session identifier (auto-generated if not provided)
        - top_k: Number of chunks to retrieve (3-10, default 5)

    Returns:
        - answer: Generated answer text
        - sources: List of source citations with chapter/section references
        - mode: Query mode ("full_book")
        - session_id: Session identifier
        - response_time_ms: Processing time in milliseconds
    """
    try:
        logger.info(f"Received query request: session_id={request.session_id}")

        # Check if demo mode is enabled
        if settings.demo_mode:
            logger.info("Demo mode enabled - returning mock response")
            demo_data = demo_service.get_demo_response(request.query)

            # Convert demo sources to SourceCitation objects
            sources = [
                SourceCitation(**src) for src in demo_data.get("sources", [])
            ]

            return QueryResponse(
                answer=demo_data["answer"],
                sources=sources,
                mode="full_book",
                session_id=request.session_id or str(uuid.uuid4()),
                response_time_ms=100
            )

        # Process through RAG pipeline
        response = rag_pipeline.process_query(request)

        logger.info(f"Query processed successfully: {response.response_time_ms}ms")
        return response

    except ValueError as e:
        logger.warning(f"Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_QUERY",
                "message": str(e)
            }
        )

    except ConnectionError as e:
        logger.error(f"Service connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "SERVICE_UNAVAILABLE",
                "message": "Vector database or AI service is temporarily unavailable. Please try again later."
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later."
            }
        )
