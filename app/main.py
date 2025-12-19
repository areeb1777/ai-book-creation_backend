"""
RAG Chatbot API - Main Application Entry Point for Vercel Deployment

This FastAPI application provides endpoints for the RAG-based chatbot
that answers questions about book content using vector similarity search.
Designed for Vercel serverless deployment with Mangum adapter.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Only load environment variables locally, not in Vercel
if not os.getenv("VERCEL"):
    from dotenv import load_dotenv
    load_dotenv()

# Initialize FastAPI app with serverless-friendly settings
app = FastAPI(
    title="RAG Chatbot API",
    description="API for book Q&A chatbot using Retrieval-Augmented Generation",
    version="1.0.0",
    docs_url="/docs",  # Access docs at /docs
    redoc_url="/redoc",  # Access redoc at /redoc
    openapi_url="/openapi.json"  # Access openapi schema at /openapi.json
)

# Configure CORS - Allow all origins for Vercel (configure more restrictively in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For Vercel deployment - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes and add them to the app
from app.api.routes import health, query, query_selected

# Add rate limiting
from app.core.security import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(query.router, tags=["Query"])
app.include_router(query_selected.router, tags=["Query"])

@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "message": "RAG Chatbot API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "environment": "production" if os.getenv("VERCEL") else "development"
    }

# Create Mangum handler for Vercel serverless functions
handler = Mangum(app)

# This allows the application to run locally with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True,
        log_level="info"
    )
