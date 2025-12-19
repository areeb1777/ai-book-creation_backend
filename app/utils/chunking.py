"""
Document Chunking Utilities

Implements semantic chunking with overlap for RAG pipeline.
Preserves context across chunk boundaries and handles special content types.
"""

import re
import tiktoken
from typing import List, Dict, Any, Tuple
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentChunker:
    """Chunk documents with semantic boundaries and overlap"""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        encoding_name: str = "cl100k_base"  # OpenAI encoding
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using OpenAI tokenizer"""
        return len(self.encoding.encode(text))

    def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk text with semantic boundaries and overlap

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Remove excessive whitespace but preserve paragraphs
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Split into paragraphs
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_tokens = self.count_tokens(para)

            # If single paragraph exceeds chunk size, split it
            if para_tokens > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0

                # Split long paragraph by sentences
                sentences = self._split_sentences(para)
                sentence_chunk = []
                sentence_tokens = 0

                for sent in sentences:
                    sent_tokens = self.count_tokens(sent)
                    if sentence_tokens + sent_tokens <= self.chunk_size:
                        sentence_chunk.append(sent)
                        sentence_tokens += sent_tokens
                    else:
                        if sentence_chunk:
                            chunks.append(' '.join(sentence_chunk))
                        sentence_chunk = [sent]
                        sentence_tokens = sent_tokens

                if sentence_chunk:
                    chunks.append(' '.join(sentence_chunk))

            # Normal paragraph fits in chunk
            elif current_tokens + para_tokens <= self.chunk_size:
                current_chunk.append(para)
                current_tokens += para_tokens
            else:
                # Current chunk is full, save it
                chunks.append('\n\n'.join(current_chunk))

                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = [overlap_text, para] if overlap_text else [para]
                current_tokens = self.count_tokens('\n\n'.join(current_chunk))

        # Save final chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        # Format as chunk dictionaries
        chunk_dicts = []
        for i, chunk_text in enumerate(chunks):
            chunk_dict = {
                "text": chunk_text,
                "chunk_index": i,
                "token_count": self.count_tokens(chunk_text)
            }

            # Add metadata if provided
            if metadata:
                chunk_dict.update(metadata)

            chunk_dicts.append(chunk_dict)

        logger.info(f"Created {len(chunk_dicts)} chunks from text ({len(text)} chars)")
        return chunk_dicts

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be enhanced with NLTK)
        sentence_endings = re.compile(r'([.!?])\s+')
        sentences = sentence_endings.split(text)

        # Rejoin sentence endings with their sentences
        result = []
        for i in range(0, len(sentences) - 1, 2):
            result.append(sentences[i] + sentences[i + 1])

        if len(sentences) % 2 == 1:
            result.append(sentences[-1])

        return [s.strip() for s in result if s.strip()]

    def _get_overlap_text(self, chunks: List[str]) -> str:
        """
        Get overlap text from previous chunks

        Args:
            chunks: List of previous chunk texts

        Returns:
            Overlap text (last N tokens from previous chunks)
        """
        if not chunks:
            return ""

        # Get last chunk
        last_chunk = chunks[-1]

        # Get last N tokens
        tokens = self.encoding.encode(last_chunk)
        if len(tokens) <= self.chunk_overlap:
            return last_chunk

        # Return last chunk_overlap tokens
        overlap_tokens = tokens[-self.chunk_overlap:]
        overlap_text = self.encoding.decode(overlap_tokens)

        return overlap_text

    def preserve_code_blocks(self, text: str) -> Tuple[str, Dict[int, str]]:
        """
        Extract and preserve code blocks to prevent splitting

        Args:
            text: Markdown text

        Returns:
            Tuple of (text with placeholders, dict mapping placeholder to code)
        """
        code_blocks = {}
        counter = 0

        def replace_code(match):
            nonlocal counter
            placeholder = f"__CODE_BLOCK_{counter}__"
            code_blocks[counter] = match.group(0)
            counter += 1
            return placeholder

        # Match code blocks (``` ... ```)
        pattern = re.compile(r'```[\s\S]*?```', re.MULTILINE)
        text_with_placeholders = pattern.sub(replace_code, text)

        return text_with_placeholders, code_blocks

    def restore_code_blocks(self, text: str, code_blocks: Dict[int, str]) -> str:
        """Restore code blocks from placeholders"""
        for i, code in code_blocks.items():
            text = text.replace(f"__CODE_BLOCK_{i}__", code)
        return text


# Global chunker instance
chunker = DocumentChunker()
