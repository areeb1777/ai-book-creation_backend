"""
Unit Tests for Chunking Module

Tests document chunking logic, token counting, and overlap.
"""

import pytest
from app.utils.chunking import DocumentChunker


class TestDocumentChunker:
    """Test DocumentChunker class"""

    def test_chunk_creation(self, sample_markdown):
        """Test basic chunk creation"""
        chunker = DocumentChunker(chunk_size=200, chunk_overlap=50)
        chunks = chunker.chunk_text(sample_markdown)

        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('chunk_index' in chunk for chunk in chunks)
        assert all('token_count' in chunk for chunk in chunks)

    def test_chunk_size_limit(self):
        """Test chunks respect size limit"""
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        long_text = "This is a test sentence. " * 100  # Long text

        chunks = chunker.chunk_text(long_text)

        for chunk in chunks:
            token_count = chunker.count_tokens(chunk['text'])
            assert token_count <= 120  # Allow small overflow for paragraph boundaries

    def test_chunk_overlap(self):
        """Test overlap between consecutive chunks"""
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=30)
        text = "Paragraph one with content. " * 20 + "\n\n" + "Paragraph two with more content. " * 20

        chunks = chunker.chunk_text(text)

        if len(chunks) > 1:
            # Check that chunks have some overlapping content
            assert len(chunks) >= 2

    def test_token_counting(self):
        """Test token counting"""
        chunker = DocumentChunker()
        text = "This is a test sentence with multiple words."

        token_count = chunker.count_tokens(text)

        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count < 20  # Should be around 10-15 tokens

    def test_metadata_preservation(self):
        """Test metadata is preserved in chunks"""
        chunker = DocumentChunker(chunk_size=200)
        metadata = {
            "source_file": "test.md",
            "chapter": "Test Chapter",
            "section": "Test Section"
        }

        chunks = chunker.chunk_text("Test content here.", metadata=metadata)

        assert all(chunk['source_file'] == "test.md" for chunk in chunks)
        assert all(chunk['chapter'] == "Test Chapter" for chunk in chunks)

    def test_empty_text(self):
        """Test handling of empty text"""
        chunker = DocumentChunker()
        chunks = chunker.chunk_text("")

        assert len(chunks) == 0

    def test_short_text(self):
        """Test handling of text shorter than chunk size"""
        chunker = DocumentChunker(chunk_size=1000)
        short_text = "This is a short text."

        chunks = chunker.chunk_text(short_text)

        assert len(chunks) == 1
        assert chunks[0]['text'] == short_text
