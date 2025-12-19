"""
API Routes Package Initialization

This module initializes the API routes for the RAG Chatbot application.
"""

from .health import router as health
from .query import router as query
from .query_selected import router as query_selected

__all__ = ["health", "query", "query_selected"]