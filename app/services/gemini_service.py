"""
Google Gemini Service

Provides embeddings and chat using Google's Gemini API (100% FREE).
"""

import time
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.core.config import settings
from app.core.logging import get_logger
from app.api.models.request import ConversationTurn

logger = get_logger(__name__)


class GeminiEmbeddingsService:
    """Generate embeddings using Gemini API (FREE)"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = "models/text-embedding-004"

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        for i, text in enumerate(texts):
            if i > 0 and i % 10 == 0:
                logger.info(f"Processing batch {i}/{len(texts)}")
                time.sleep(0.1)  # Rate limiting

            embedding = self.generate_embedding(text)
            embeddings.append(embedding)

        return embeddings


class GeminiChatService:
    """Generate chat responses using Gemini API (FREE)"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        self.system_prompt = """You are a helpful assistant answering questions about a book.

CRITICAL INSTRUCTIONS:
1. Answer ONLY based on the provided context excerpts below.
2. If the context doesn't contain enough information to answer the question, respond: "I couldn't find information about that in this book."
3. Always cite the source (chapter and section) in your answer when referencing specific information.
4. Be concise but complete.
5. Do NOT use any external knowledge or make assumptions beyond what's in the context.

Format your citations like: "According to Chapter X, Section Y, ..."
"""

    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[ConversationTurn]] = None
    ) -> str:
        """
        Generate answer from query and retrieved chunks

        Args:
            query: User's question
            context_chunks: Retrieved chunks with metadata
            conversation_history: Previous conversation turns

        Returns:
            Generated answer text
        """
        # Build context from chunks
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            metadata = chunk.get('metadata', {})
            chapter = metadata.get('chapter', 'Unknown')
            section = metadata.get('section', '')
            text = chunk.get('text', '')

            context_parts.append(
                f"[Source {i}] Chapter: {chapter}"
                + (f", Section: {section}" if section else "")
                + f"\n{text}\n"
            )

        context_text = "\n---\n".join(context_parts)

        # Build conversation history
        history_text = ""
        if conversation_history:
            for turn in conversation_history[-3:]:  # Last 3 turns
                history_text += f"{turn.role.upper()}: {turn.content}\n"

        # Compose prompt
        prompt = f"""{self.system_prompt}

CONTEXT FROM BOOK:
{context_text}

{history_text}
USER: {query}

ASSISTANT:"""

        # Generate response
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise
