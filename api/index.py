"""
Vercel Serverless Function Entry Point for RAG Chatbot API

This file serves as the entry point for Vercel's serverless deployment.
It wraps the FastAPI application to work with Vercel's Python runtime.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.security import limiter
from app.api.routes import health, query, query_selected
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="API for book Q&A chatbot using Retrieval-Augmented Generation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS - Allow all origins for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(query_selected.router, prefix="/api", tags=["Query"])

@app.get("/")
@app.get("/api")
async def root():
    """Root endpoint - API status"""
    return {
        "message": "RAG Chatbot API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

# Vercel serverless handler
handler = Mangum(app, lifespan="off")
