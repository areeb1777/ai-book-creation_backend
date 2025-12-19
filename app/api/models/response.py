"""
API Response Models

Pydantic models for API responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from app.api.models.request import QueryMode


class SourceCitation(BaseModel):
    """Source citation for an answer"""

    chapter: str = Field(..., max_length=200, description="Chapter title")
    section: Optional[str] = Field(None, max_length=200, description="Section title")
    file: str = Field(..., pattern=r".*\.md$", description="Source markdown file")
    url: str = Field(..., pattern=r"^/docs/.*", description="Deep link to section")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity (0-1)")
    excerpt: Optional[str] = Field(None, max_length=500, description="Text snippet from source")


class QueryResponse(BaseModel):
    """Response model for query endpoints"""

    answer: str = Field(
        ...,
        min_length=20,
        max_length=2000,
        description="Generated answer"
    )
    sources: List[SourceCitation] = Field(
        default_factory=list,
        description="Source citations (empty if no sources found)"
    )
    mode: QueryMode = Field(..., description="Query mode used")
    session_id: UUID = Field(..., description="Session identifier")
    response_time_ms: int = Field(
        ...,
        ge=0,
        le=10000,
        description="Processing time in milliseconds"
    )
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Answer confidence score (future feature)"
    )


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error context")
