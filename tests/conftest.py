"""
Pytest Configuration and Fixtures

Provides shared test fixtures for unit and integration tests.
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import List, Dict, Any


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    client = Mock()

    # Mock embeddings.create response
    mock_embedding_response = Mock()
    mock_embedding_response.data = [
        Mock(embedding=[0.1] * 1536)  # Mock 1536-dim vector
    ]
    client.embeddings.create.return_value = mock_embedding_response

    # Mock chat.completions.create response
    mock_chat_response = Mock()
    mock_chat_response.choices = [
        Mock(message=Mock(content="This is a test answer"))
    ]
    client.chat.completions.create.return_value = mock_chat_response

    return client


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for testing"""
    client = Mock()

    # Mock search response
    mock_result = Mock()
    mock_result.id = "test-chunk-1"
    mock_result.score = 0.92
    mock_result.payload = {
        "text": "Test chunk content about Spec-Kit Plus",
        "chapter": "Chapter 1",
        "section": "Introduction",
        "source_file": "chapter-1-spec-kit.md",
        "heading_path": ["Chapter 1", "Introduction"],
        "chunk_index": 0
    }

    client.search.return_value = [mock_result]

    # Mock collection info
    mock_collection = Mock()
    mock_collection.points_count = 1000
    client.get_collection.return_value = mock_collection

    return client


@pytest.fixture
def mock_neon_client():
    """Mock Neon Postgres client for testing"""
    client = Mock()
    client.log_query.return_value = "test-log-id"
    client.test_connection.return_value = True
    return client


@pytest.fixture
def sample_chunks() -> List[Dict[str, Any]]:
    """Sample document chunks for testing"""
    return [
        {
            "text": "Spec-Kit Plus is a structured workflow for AI-assisted development.",
            "chapter": "Chapter 1",
            "section": "Introduction to Spec-Kit Plus",
            "source_file": "chapter-1-spec-kit.md",
            "heading_path": ["Chapter 1", "Introduction to Spec-Kit Plus"],
            "chunk_index": 0,
            "score": 0.92
        },
        {
            "text": "Claude Code is an AI coding assistant that helps developers write code.",
            "chapter": "Chapter 2",
            "section": "Getting Started with Claude Code",
            "source_file": "chapter-2-claude-code.md",
            "heading_path": ["Chapter 2", "Getting Started with Claude Code"],
            "chunk_index": 0,
            "score": 0.85
        }
    ]


@pytest.fixture
def sample_markdown() -> str:
    """Sample markdown content for testing"""
    return """# Chapter 1: Introduction

## Getting Started

This is the introduction section with some content.

## Installation

Here are the installation steps:

1. Step one
2. Step two
3. Step three

### Prerequisites

You need Python 3.11 or higher.

## Configuration

Configure your environment with these settings.
"""


@pytest.fixture
def sample_query_request() -> Dict[str, Any]:
    """Sample query request payload"""
    return {
        "query": "What is Spec-Kit Plus and how do I use it?",
        "conversation_history": [],
        "top_k": 5
    }
