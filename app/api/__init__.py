"""
API Package Initialization

This module initializes the API package for the RAG Chatbot application.
"""

# Import all route modules to make them available when importing the package
from . import routes

__all__ = ["routes"]