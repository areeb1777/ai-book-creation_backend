"""
Security Utilities

Input sanitization, rate limiting, and API key authentication.
"""

import re
from typing import Optional
from fastapi import Header, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def sanitize_query(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks

    Args:
        text: Raw user input

    Returns:
        Sanitized text

    Removes:
        - SQL injection patterns (', ", \, ;)
        - XSS patterns (<script>, HTML tags)
        - Excessive whitespace
    """
    # Remove potential SQL injection patterns
    sanitized = re.sub(r"[';\"\\\\]", "", text)

    # Remove XSS patterns
    sanitized = re.sub(r"<script.*?>.*?</script>", "", sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r"<.*?>", "", sanitized)

    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized)

    # Trim
    sanitized = sanitized.strip()

    return sanitized


def validate_query_length(text: str, min_words: int = 3, max_words: int = 500) -> bool:
    """
    Validate query has appropriate word count

    Args:
        text: Query text
        min_words: Minimum word count
        max_words: Maximum word count

    Returns:
        True if valid, raises ValueError otherwise
    """
    words = text.split()
    word_count = len(words)

    if word_count < min_words:
        raise ValueError(f"Query must contain at least {min_words} words (found {word_count})")

    if word_count > max_words:
        raise ValueError(f"Query must contain at most {max_words} words (found {word_count})")

    return True


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """
    Verify API key if authentication is enabled

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        True if valid or auth disabled

    Raises:
        HTTPException: 401 if invalid or missing
    """
    # If API_KEY not set in environment, authentication is disabled
    if not settings.api_key:
        return True

    # API key required but not provided
    if not x_api_key:
        logger.warning("API key required but not provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "UNAUTHORIZED",
                "message": "API key required. Provide X-API-Key header."
            }
        )

    # Verify API key matches
    if x_api_key != settings.api_key:
        logger.warning(f"Invalid API key provided: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "UNAUTHORIZED",
                "message": "Invalid API key."
            }
        )

    return True


def get_rate_limit_string() -> str:
    """Get rate limit string for slowapi"""
    return f"{settings.rate_limit_per_hour}/hour"


# Rate limit decorator factory
def rate_limit(limit: str = None):
    """
    Apply rate limiting to endpoint

    Args:
        limit: Rate limit string (e.g., "100/hour")
                If not provided, uses settings.rate_limit_per_hour

    Usage:
        @app.post("/api/query")
        @rate_limit()
        async def query_endpoint(...):
            ...
    """
    limit_str = limit or get_rate_limit_string()
    return limiter.limit(limit_str)
