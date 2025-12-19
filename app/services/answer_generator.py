"""
Answer Generator Service

Generates answers using OpenAI Chat Completions API with retrieved context.
Ensures answers are grounded in book content only (no hallucination).
"""

from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.core.config import settings
from app.core.logging import get_logger
from app.api.models.request import ConversationTurn

logger = get_logger(__name__)


class AnswerGenerator:
    """Service for generating RAG-based answers"""

    def __init__(self):
        # Check if using Gemini
        gemini_key = getattr(settings, 'gemini_api_key', None)
        if gemini_key:
            from app.services.gemini_service import GeminiChatService
            self.backend = GeminiChatService(gemini_key)
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
            self.model = settings.openai_chat_model
            self.use_gemini = False

        # System prompt for grounded answers
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
        # Use Gemini if configured
        if self.use_gemini:
            return self.backend.generate_answer(query, context_chunks, conversation_history)

        # Format context from chunks
        context = self._format_context(context_chunks)

        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add conversation history
        if conversation_history:
            for turn in conversation_history[-2:]:  # Last 2 turns only
                messages.append({
                    "role": turn.role,
                    "content": turn.content
                })

        # Add context and query
        user_message = f"""Context:
---
{context}
---

Question: {query}

Answer:"""

        messages.append({"role": "user", "content": user_message})

        # Generate answer
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Low but not zero (allow some creativity)
                max_tokens=500,   # Concise answers
                top_p=1.0
            )

            answer = response.choices[0].message.content.strip()

            logger.info(f"Generated answer ({len(answer)} chars)")
            return answer

        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            raise

    def generate_from_selected_text(
        self,
        query: str,
        selected_text: str
    ) -> str:
        """
        Generate answer using only selected text (no vector search)

        Args:
            query: User's question
            selected_text: User-selected text from book

        Returns:
            Generated answer with disclaimer
        """
        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        user_message = f"""Context (user-selected text):
---
{selected_text}
---

Question: {query}

Answer ONLY based on the selected text above. If the selected text doesn't contain the answer, say so.

Answer:"""

        messages.append({"role": "user", "content": user_message})

        # Generate answer
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=500,
                top_p=1.0
            )

            answer = response.choices[0].message.content.strip()

            # Prepend disclaimer
            answer_with_disclaimer = f"Based on your selected text: {answer}"

            logger.info(f"Generated selected-text answer ({len(answer)} chars)")
            return answer_with_disclaimer

        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            raise

    def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks as context for prompt

        Args:
            chunks: List of chunk dictionaries with text and metadata

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context found."

        context_parts = []

        for chunk in chunks:
            # Build header with chapter and section
            header_parts = []
            if chunk.get("chapter"):
                header_parts.append(chunk["chapter"])
            if chunk.get("section"):
                header_parts.append(chunk["section"])

            header = ", ".join(header_parts) if header_parts else chunk.get("source_file", "Unknown")

            # Format as: [Chapter X, Section Y]
            context_parts.append(f"[{header}]")
            context_parts.append(chunk["text"])
            context_parts.append("")  # Empty line between chunks

        return "\n".join(context_parts)


# Global service instance
answer_generator = AnswerGenerator()
