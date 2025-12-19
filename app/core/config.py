"""
Configuration Management

Loads and validates environment variables using Pydantic Settings.
Provides type-safe access to configuration throughout the application.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    demo_mode: bool = False  # Set to True to use mock responses (no API costs)

    # AI Provider Configuration
    # Option 1: Google Gemini (FREE - Recommended)
    gemini_api_key: Optional[str] = None  # Get from: https://aistudio.google.com/app/apikey

    # Option 2: OpenAI or OpenRouter (Paid)
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None  # For OpenRouter: https://openrouter.ai/api/v1
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-3.5-turbo-0125"

    # Qdrant Configuration
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "book_chunks"

    # Neon Postgres Configuration
    database_url: str

    # API Configuration
    api_key: Optional[str] = None  # Optional: for production authentication
    cors_origins: str = "http://localhost:3000"
    rate_limit_per_hour: int = 100

    # Logging
    sentry_dsn: Optional[str] = None

    # RAG Configuration
    chunk_size: int = 800  # tokens
    chunk_overlap: int = 100  # tokens
    top_k: int = 5  # number of chunks to retrieve
    similarity_threshold: float = 0.3  # minimum cosine similarity (lowered for Gemini compatibility)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    def get_cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
