"""
Embeddings Service

Generates vector embeddings using OpenAI, OpenRouter, or Google Gemini API.
"""

import time
from typing import List
from openai import OpenAI
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingsService:
    """Service for generating embeddings"""

    def __init__(self):
        # Check if using Gemini
        gemini_key = getattr(settings, 'gemini_api_key', None)
        if gemini_key:
            logger.info("Using Google Gemini for embeddings")
            from app.services.gemini_service import GeminiEmbeddingsService
            self.backend = GeminiEmbeddingsService(gemini_key)
            self.use_gemini = True
        else:
            # Support OpenRouter by setting custom base_url
            base_url = getattr(settings, 'openai_base_url', None)
            if base_url:
                self.client = OpenAI(
                    api_key=settings.openai_api_key,
                    base_url=base_url,
                    default_headers={
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "AI Book Chatbot"
                    }
                )
            else:
                self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_embedding_model
            self.use_gemini = False

        self.max_retries = 3
        self.batch_size = 100  # OpenAI allows up to 2048

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for single text

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        if self.use_gemini:
            return self.backend.generate_embedding(text)
        return self.generate_embeddings([text])[0]

    def generate_embeddings(
        self,
        texts: List[str],
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with batch processing

        Args:
            texts: List of texts to embed
            show_progress: Whether to log progress

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Use Gemini if configured
        if self.use_gemini:
            return self.backend.generate_embeddings(texts)

        all_embeddings = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1

            if show_progress:
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")

            # Generate embeddings with retry logic
            embeddings = self._generate_batch_with_retry(batch)
            all_embeddings.extend(embeddings)

        logger.info(f"✅ Generated {len(all_embeddings)} embeddings")
        return all_embeddings

    def _generate_batch_with_retry(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for batch with exponential backoff retry

        Args:
            texts: Batch of texts

        Returns:
            List of embedding vectors
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts,
                    encoding_format="float"
                )

                # Extract embeddings from response
                embeddings = [item.embedding for item in response.data]

                # Verify dimensions
                if embeddings and len(embeddings[0]) != 1536:
                    logger.warning(f"Unexpected embedding dimension: {len(embeddings[0])}")

                return embeddings

            except Exception as e:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(f"Embedding generation failed (attempt {attempt + 1}/{self.max_retries}): {e}")

                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to generate embeddings after {self.max_retries} attempts")
                    raise

    def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            test_embedding = self.generate_embedding("test")
            return len(test_embedding) == 1536
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False


# Global service instance
embeddings_service = EmbeddingsService()
