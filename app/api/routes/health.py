"""
Health Check Endpoint

Provides service health status and dependency checks.
Used for monitoring and deployment readiness verification.
"""

from fastapi import APIRouter, status
from typing import Dict, Any
from app.services.vector_store import vector_store
from app.services.metadata_store import neon_client
from app.core.config import settings
from app.core.logging import get_logger
import openai

logger = get_logger(__name__)
router = APIRouter()


def check_openai() -> str:
    """Check OpenAI API key validity"""
    try:
        # Test with a simple API call
        client = openai.OpenAI(api_key=settings.openai_api_key)
        # List models to verify API key
        models = client.models.list()
        return "api_key_valid"
    except openai.AuthenticationError:
        return "api_key_invalid"
    except Exception as e:
        logger.error(f"OpenAI check failed: {e}")
        return "error"


def check_qdrant() -> str:
    """Check Qdrant connection"""
    try:
        if vector_store.test_connection():
            return "connected"
        else:
            return "collection_not_found"
    except Exception as e:
        logger.error(f"Qdrant check failed: {e}")
        return "disconnected"


def check_neon() -> str:
    """Check Neon Postgres connection"""
    try:
        if neon_client.test_connection():
            return "connected"
        else:
            return "disconnected"
    except Exception as e:
        logger.error(f"Neon check failed: {e}")
        return "disconnected"


@router.get(
    "/api/health",
    response_model=Dict[str, Any],
    summary="Health Check",
    description="Check API and service health status"
)
async def health_check():
    """
    Health check endpoint

    Returns:
        - status: Overall health (healthy/degraded/unhealthy)
        - services: Status of each dependency
        - version: API version
        - uptime_seconds: Service uptime (placeholder)

    Status Codes:
        - 200: Service is healthy or degraded but operational
        - 503: Service is unhealthy
    """

    # Check all services
    services_status = {
        "qdrant": check_qdrant(),
        "neon": check_neon(),
        "openai": check_openai()
    }

    # Determine overall status
    connected_count = sum(1 for s in services_status.values() if s in ["connected", "api_key_valid"])

    if connected_count == 3:
        overall_status = "healthy"
        http_status = status.HTTP_200_OK
    elif connected_count >= 1:
        overall_status = "degraded"
        http_status = status.HTTP_200_OK
    else:
        overall_status = "unhealthy"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    response = {
        "status": overall_status,
        "services": services_status,
        "version": "1.0.0",
        "uptime_seconds": 0  # TODO: Implement actual uptime tracking
    }

    # Log degraded/unhealthy status
    if overall_status != "healthy":
        logger.warning(f"Health check: {overall_status} - {services_status}")

    return response
