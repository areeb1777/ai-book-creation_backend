"""
Export Neon Database Schema

Exports the database schema to SQL file for backup purposes.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def export_schema():
    """Export schema by reading the source SQL file"""
    schema_file = Path(__file__).parent.parent / "app" / "core" / "database_schema.sql"
    output_file = Path(__file__).parent.parent.parent / "backup" / "schemas" / "neon_schema.sql"

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Copy schema file
    with open(schema_file, 'r') as src:
        schema_content = src.read()

    with open(output_file, 'w') as dst:
        dst.write(schema_content)

    print(f"Schema exported to {output_file}")

    return str(output_file)


if __name__ == "__main__":
    export_schema()
