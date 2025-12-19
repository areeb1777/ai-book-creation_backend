"""
RAG Chatbot API - Main Application Entry Point for Vercel Deployment

This FastAPI application provides endpoints for the RAG-based chatbot
that answers questions about book content using vector similarity search.
Designed for Vercel serverless deployment with Mangum adapter.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from dotenv import load_dotenv
import os

# Load environment variables (only in non-serverless environments if needed)
if os.getenv("VERCEL") != "1":
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

# Dynamically import routes to avoid cold start issues if needed
def import_routes():
    from app.api.routes import health, query, query_selected
    from app.core.security import limiter
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded

    # Add rate limiter state
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Include routers
    app.include_router(health.router, prefix="", tags=["Health"])
    app.include_router(query.router, prefix="", tags=["Query"])
    app.include_router(query_selected.router, prefix="", tags=["Query"])

# Call import_routes to set up routes
import_routes()

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
handler = Mangum(app, lifespan="on")

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
