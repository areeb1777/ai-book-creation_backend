"""
Structured Logging Configuration

Provides JSON-formatted logging with automatic redaction of sensitive data.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs JSON logs"""

    SENSITIVE_FIELDS = {
        "api_key", "password", "token", "secret", "authorization",
        "openai_api_key", "qdrant_api_key", "database_url"
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra context from record
        if hasattr(record, "context"):
            context = record.context
            # Redact sensitive fields
            log_data["context"] = self._redact_sensitive(context)

        # Add request_id if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)

    def _redact_sensitive(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive fields from log data"""
        redacted = {}
        for key, value in data.items():
            if key.lower() in self.SENSITIVE_FIELDS:
                redacted[key] = "[REDACTED]"
            elif isinstance(value, dict):
                redacted[key] = self._redact_sensitive(value)
            else:
                redacted[key] = value
        return redacted


def setup_logging():
    """Configure application logging"""
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove existing handlers
    root_logger.handlers = []

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level.upper()))

    # Use JSON formatter for production, simple formatter for development
    if settings.environment == "production":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return root_logger


# Initialize logging
logger = setup_logging()


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module"""
    return logging.getLogger(name)
