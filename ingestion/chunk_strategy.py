"""
Chunk Strategy

Defines chunk metadata structure and ingestion strategies.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class ChunkMetadata:
    """Metadata for a document chunk"""

    text: str
    chapter: str
    section: str
    source_file: str
    heading_path: List[str]
    chunk_index: int
    page_number: Optional[int] = None
    token_count: Optional[int] = None
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            "text": self.text,
            "chapter": self.chapter,
            "section": self.section,
            "source_file": self.source_file,
            "heading_path": self.heading_path,
            "chunk_index": self.chunk_index,
            "page_number": self.page_number,
            "token_count": self.token_count,
            "created_at": self.created_at
        }


def create_chunk_metadata(
    text: str,
    source_file: str,
    chapter: str,
    section: str,
    chunk_index: int,
    heading_path: List[str],
    page_number: Optional[int] = None,
    token_count: Optional[int] = None
) -> ChunkMetadata:
    """
    Factory function to create chunk metadata

    Args:
        text: Chunk text content
        source_file: Source markdown filename
        chapter: Chapter title (H1)
        section: Section title (H2)
        chunk_index: Position in document
        heading_path: Full heading hierarchy
        page_number: Estimated page number
        token_count: Number of tokens in chunk

    Returns:
        ChunkMetadata instance
    """
    return ChunkMetadata(
        text=text,
        chapter=chapter,
        section=section,
        source_file=source_file,
        heading_path=heading_path,
        chunk_index=chunk_index,
        page_number=page_number,
        token_count=token_count
    )
