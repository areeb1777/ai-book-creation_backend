"""
Selected Text Query Endpoint

POST /api/query/selected - Answer questions using only user-selected text.
"""

import time
from fastapi import APIRouter, HTTPException, status
from app.api.models.request import QuerySelectedRequest
from app.api.models.response import QueryResponse, ErrorResponse
from app.services.answer_generator import answer_generator
from app.services.metadata_store import neon_client
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/api/query/selected",
    response_model=QueryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    },
    summary="Query selected text",
    description="Answer question using only user-selected text (no vector search)"
)
async def query_selected_text(request: QuerySelectedRequest):
    """
    Query using only selected text

    Generates answer based exclusively on user-selected text from the book page.
    No vector search is performed - answer is constrained to provided text only.

    Request Body:
        - query: User's question about the selected text
        - selected_text: Text selected by user (min 20 chars)
        - session_id: Optional session identifier

    Returns:
        - answer: Generated answer with disclaimer "Based on your selected text..."
        - sources: Empty list (no vector search)
        - mode: "selected_text"
        - session_id: Session identifier
        - response_time_ms: Processing time
    """
    start_time = time.time()

    try:
        logger.info(f"Received selected-text query: session_id={request.session_id}")

        # Validate selected text length
        if len(request.selected_text.strip()) < 20:
            raise ValueError("Selected text is too short. Please select at least one complete sentence.")

        # Generate answer using only selected text (no vector search)
        logger.info("Generating answer from selected text...")
        answer_text = answer_generator.generate_from_selected_text(
            query=request.query,
            selected_text=request.selected_text
        )

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)

        # Log query and answer
        neon_client.log_query(
            session_id=request.session_id,
            query_text=request.query,
            query_mode="selected_text",
            answer_text=answer_text,
            source_chunks=[],  # No sources in selected-text mode
            response_time_ms=response_time_ms,
            selected_text=request.selected_text
        )

        # Return response
        response = QueryResponse(
            answer=answer_text,
            sources=[],  # No sources for selected-text mode
            mode="selected_text",
            session_id=request.session_id,
            response_time_ms=response_time_ms
        )

        logger.info(f"Selected-text query processed: {response_time_ms}ms")
        return response

    except ValueError as e:
        logger.warning(f"Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_REQUEST",
                "message": str(e)
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error processing selected-text query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later."
            }
        )
