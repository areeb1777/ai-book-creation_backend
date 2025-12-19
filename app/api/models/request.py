"""
API Request Models

Pydantic models for API request validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum
from uuid import UUID, uuid4


class QueryMode(str, Enum):
    """Query mode enum"""
    FULL_BOOK = "full_book"
    SELECTED_TEXT = "selected_text"


class ConversationTurn(BaseModel):
    """Single turn in conversation history"""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=2000)


class QueryRequest(BaseModel):
    """Request model for full-book query"""

    query: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="User's natural language question"
    )
    query_mode: QueryMode = Field(
        default=QueryMode.FULL_BOOK,
        description="Query mode: full_book or selected_text"
    )
    conversation_history: List[ConversationTurn] = Field(
        default_factory=list,
        max_length=10,
        description="Previous conversation turns for context"
    )
    session_id: Optional[UUID] = Field(
        default_factory=uuid4,
        description="Session identifier"
    )
    top_k: int = Field(
        default=5,
        ge=3,
        le=10,
        description="Number of chunks to retrieve"
    )

    @field_validator('query')
    @classmethod
    def validate_query_length(cls, v: str) -> str:
        """Ensure query has minimum word count"""
        word_count = len(v.split())
        if word_count < 3:
            raise ValueError("Query must contain at least 3 words")
        if word_count > 500:
            raise ValueError("Query must contain at most 500 words")
        return v


class QuerySelectedRequest(BaseModel):
    """Request model for selected-text query"""

    query: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="User's question about selected text"
    )
    selected_text: str = Field(
        ...,
        min_length=20,
        max_length=5000,
        description="Text selected by user (at least one sentence)"
    )
    session_id: Optional[UUID] = Field(
        default_factory=uuid4,
        description="Session identifier"
    )

    @field_validator('query')
    @classmethod
    def validate_query_length(cls, v: str) -> str:
        """Ensure query has minimum word count"""
        word_count = len(v.split())
        if word_count < 3:
            raise ValueError("Query must contain at least 3 words")
        return v

    @field_validator('selected_text')
    @classmethod
    def validate_selected_text(cls, v: str) -> str:
        """Ensure selected text has minimum length"""
        if len(v.strip()) < 20:
            raise ValueError("Selected text must be at least 20 characters (approximately one sentence)")
        return v
