"""
Demo Mode Service

Provides mock responses for testing without API costs.
Returns pre-written answers about the book for common questions.
"""

from typing import List, Dict, Any
from app.api.models.response import SourceCitation

# Sample responses for demo mode
DEMO_RESPONSES = {
    "what is this book about": {
        "answer": "This book is a comprehensive guide to AI-assisted book creation using Spec-Kit Plus and Claude Code. It teaches you how to leverage AI agents for specification-driven development, from initial planning through implementation. The book covers creating specifications, planning architectures, generating tasks, and implementing features using structured workflows.",
        "sources": [
            {
                "chapter": "Introduction",
                "section": "Overview",
                "file": "intro.md",
                "url": "/docs/intro",
                "similarity_score": 0.95,
                "excerpt": "Master the art of AI-enhanced content creation..."
            }
        ]
    },
    "spec-kit plus": {
        "answer": "Spec-Kit Plus is a specification-driven development framework that helps you build software systematically. It provides templates, workflows, and agents for creating detailed specifications, architectural plans, and implementation tasks. The framework emphasizes clear documentation, architectural decision records, and test-driven development.",
        "sources": [
            {
                "chapter": "Chapter 1",
                "section": "What is Spec-Kit Plus",
                "file": "chapter-1.md",
                "url": "/docs/chapter-1",
                "similarity_score": 0.92,
                "excerpt": "Spec-Kit Plus framework overview..."
            }
        ]
    },
    "constitution": {
        "answer": "The constitution in Spec-Kit Plus is a project-wide document that defines coding standards, architectural principles, testing requirements, and development guidelines. It serves as the source of truth for how code should be written and ensures consistency across the entire project.",
        "sources": [
            {
                "chapter": "Chapter 2",
                "section": "Project Constitution",
                "file": "chapter-2.md",
                "url": "/docs/chapter-2",
                "similarity_score": 0.90,
                "excerpt": "Constitution defines project principles..."
            }
        ]
    }
}

DEFAULT_RESPONSE = {
    "answer": "I'm running in demo mode! This is a sample response. To get real answers from your book content, you need to add credit to your OpenRouter account ($5 minimum) for embedding generation. The chat model is free, but embeddings cost about $0.01 per 100 queries.",
    "sources": []
}


class DemoModeService:
    """Provides mock responses for testing"""

    def get_demo_response(self, query: str) -> Dict[str, Any]:
        """
        Get a demo response based on query keywords

        Args:
            query: User's question

        Returns:
            Dict with 'answer' and 'sources' keys
        """
        query_lower = query.lower()

        # Check for keyword matches
        for keyword, response in DEMO_RESPONSES.items():
            if keyword in query_lower:
                return response

        # Default response
        return DEFAULT_RESPONSE


# Singleton instance
demo_service = DemoModeService()
