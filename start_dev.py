#!/usr/bin/env python3
"""
Development startup script for the RAG Chatbot API.

This script starts the FastAPI application using uvicorn for local development.
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Start the FastAPI application."""
    # Add the rag-backend directory to the Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Set the PYTHONPATH environment variable
    os.environ.setdefault('PYTHONPATH', str(current_dir))
    
    print("Starting RAG Chatbot API...")
    print("Docs available at: http://localhost:8000/docs")
    print("Redoc available at: http://localhost:8000/redoc")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()