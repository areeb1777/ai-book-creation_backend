"""
Document Ingestion Pipeline

Processes markdown files from book docs directory,
chunks content, generates embeddings, and stores in Qdrant.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List
from app.utils.markdown_parser import markdown_parser
from app.utils.chunking import chunker
from app.services.embeddings import embeddings_service
from app.services.vector_store import vector_store
from app.services.metadata_store import neon_client
from app.core.logging import get_logger
from ingestion.chunk_strategy import create_chunk_metadata

logger = get_logger(__name__)


class IngestionPipeline:
    """Pipeline for ingesting book content into vector database"""

    def __init__(self, source_dir: str = None):
        self.source_dir = Path(source_dir or "ai-powered-book/docs")
        self.total_chunks = 0
        self.total_files = 0

    def run(self):
        """Execute full ingestion pipeline"""
        logger.info("="  * 60)
        logger.info("Starting Document Ingestion Pipeline")
        logger.info("=" * 60)

        # Start ingestion log
        log_id = neon_client.start_ingestion_log(metadata={
            "source_dir": str(self.source_dir),
            "chunk_size": chunker.chunk_size,
            "chunk_overlap": chunker.chunk_overlap,
            "embedding_model": embeddings_service.model
        })

        try:
            # Get all markdown files
            md_files = self._discover_markdown_files()
            logger.info(f"Found {len(md_files)} markdown files")

            if not md_files:
                raise ValueError(f"No markdown files found in {self.source_dir}")

            # Process each file
            all_chunks = []
            for file_path in md_files:
                logger.info(f"\nProcessing: {file_path.name}")
                chunks = self._process_file(file_path)
                all_chunks.extend(chunks)
                self.total_files += 1

            self.total_chunks = len(all_chunks)
            logger.info(f"\n✅ Created {self.total_chunks} chunks from {self.total_files} files")

            # Generate embeddings
            logger.info("\nGenerating embeddings...")
            chunk_texts = [chunk["text"] for chunk in all_chunks]
            embeddings = embeddings_service.generate_embeddings(chunk_texts)

            # Store in Qdrant
            logger.info("\nStoring in Qdrant...")
            vector_store.upsert_chunks(all_chunks, embeddings)

            # Complete ingestion log
            neon_client.complete_ingestion_log(
                log_id=log_id,
                total_chunks=self.total_chunks,
                total_files=self.total_files
            )

            logger.info("\n" + "=" * 60)
            logger.info("✅ Ingestion Pipeline Completed Successfully!")
            logger.info("=" * 60)
            logger.info(f"Total files: {self.total_files}")
            logger.info(f"Total chunks: {self.total_chunks}")
            logger.info(f"Average chunks/file: {self.total_chunks / self.total_files:.1f}")

            return True

        except Exception as e:
            logger.error(f"\n❌ Ingestion failed: {e}")

            # Log failure
            neon_client.complete_ingestion_log(
                log_id=log_id,
                total_chunks=self.total_chunks,
                total_files=self.total_files,
                error_message=str(e)
            )

            return False

    def _discover_markdown_files(self) -> List[Path]:
        """Discover all markdown files in source directory"""
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source_dir}")

        md_files = list(self.source_dir.glob("*.md"))

        # Sort by filename for consistent processing
        md_files.sort()

        return md_files

    def _process_file(self, file_path: Path) -> List[dict]:
        """
        Process single markdown file

        Args:
            file_path: Path to markdown file

        Returns:
            List of chunk dictionaries
        """
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove frontmatter (YAML metadata)
        content = markdown_parser.remove_frontmatter(content)

        # Extract heading hierarchy
        chapter, section = markdown_parser.extract_chapter_and_section(content)
        heading_path = markdown_parser.get_heading_path(content)

        logger.info(f"  Chapter: {chapter or 'N/A'}")
        logger.info(f"  Section: {section or 'N/A'}")

        # Chunk the content
        chunks = chunker.chunk_text(
            text=content,
            metadata={
                "source_file": file_path.name,
                "chapter": chapter or file_path.stem,
                "section": section or "",
                "heading_path": heading_path or [file_path.stem]
            }
        )

        logger.info(f"  Created {len(chunks)} chunks")

        return chunks


def main(source_dir: str = None):
    """Main entry point for ingestion"""
    pipeline = IngestionPipeline(source_dir)
    success = pipeline.run()

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest book content into vector database")
    parser.add_argument(
        "--source",
        type=str,
        help="Source directory containing markdown files",
        default="ai-powered-book/docs"
    )

    args = parser.parse_args()
    main(args.source)
