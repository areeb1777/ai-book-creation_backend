"""
Run Ingestion Pipeline

Wrapper script to execute document ingestion with proper error handling.

Usage:
    python scripts/run_ingestion.py
    python scripts/run_ingestion.py --source backup/docs
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.ingest import main


if __name__ == "__main__":
    print("=" * 60)
    print("RAG Chatbot - Document Ingestion Pipeline")
    print("=" * 60)
    print()

    # Get source directory from command line or use default
    source_dir = sys.argv[1] if len(sys.argv) > 1 else "../ai-powered-book/docs"

    print(f"Source directory: {source_dir}")
    print()
    print("Processing all markdown files and updating vector database...")
    print()

    # Run ingestion
    main(source_dir)
