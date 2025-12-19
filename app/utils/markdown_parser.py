"""
Markdown Parser

Extracts headings and hierarchy from Docusaurus markdown files.
Parses H1 (chapter), H2 (section), H3 (subsection) structure.
"""

import re
from typing import List, Dict, Tuple, Any
from pathlib import Path
from app.core.logging import get_logger

logger = get_logger(__name__)


class MarkdownParser:
    """Parse markdown files and extract structure"""

    def __init__(self):
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    def extract_headings(self, content: str) -> List[Dict[str, str]]:
        """
        Extract all headings from markdown content

        Args:
            content: Markdown text

        Returns:
            List of {level, text, line_number} dictionaries
        """
        headings = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            match = self.heading_pattern.match(line)
            if match:
                level = len(match.group(1))  # Count # symbols
                text = match.group(2).strip()
                headings.append({
                    "level": level,
                    "text": text,
                    "line_number": i + 1
                })

        return headings

    def get_heading_hierarchy(self, content: str) -> Dict[str, str]:
        """
        Extract heading hierarchy from markdown

        Args:
            content: Markdown text

        Returns:
            Dictionary with h1, h2, h3 keys (chapter, section, subsection)
        """
        headings = self.extract_headings(content)

        hierarchy = {
            "h1": "",  # Chapter
            "h2": "",  # Section
            "h3": ""   # Subsection
        }

        for heading in headings:
            level = heading["level"]
            text = heading["text"]

            if level == 1:
                hierarchy["h1"] = text
                hierarchy["h2"] = ""  # Reset lower levels
                hierarchy["h3"] = ""
            elif level == 2:
                hierarchy["h2"] = text
                hierarchy["h3"] = ""  # Reset lower level
            elif level == 3:
                hierarchy["h3"] = text

        return hierarchy

    def extract_chapter_and_section(self, content: str) -> Tuple[str, str]:
        """
        Extract chapter (H1) and section (H2) from markdown

        Args:
            content: Markdown text

        Returns:
            Tuple of (chapter, section)
        """
        headings = self.extract_headings(content)

        chapter = ""
        section = ""

        for heading in headings:
            if heading["level"] == 1 and not chapter:
                chapter = heading["text"]
            elif heading["level"] == 2 and not section:
                section = heading["text"]

        return chapter, section

    def get_heading_path(self, content: str) -> List[str]:
        """
        Get full heading path as list

        Args:
            content: Markdown text

        Returns:
            List of headings from H1 to H3 (e.g., ['Chapter 1', 'Introduction', 'Getting Started'])
        """
        hierarchy = self.get_heading_hierarchy(content)

        path = []
        if hierarchy["h1"]:
            path.append(hierarchy["h1"])
        if hierarchy["h2"]:
            path.append(hierarchy["h2"])
        if hierarchy["h3"]:
            path.append(hierarchy["h3"])

        return path

    def split_by_headings(self, content: str) -> List[Dict[str, Any]]:
        """
        Split markdown into sections by H2 headings

        Args:
            content: Markdown text

        Returns:
            List of {heading, content, level} dictionaries
        """
        sections = []
        lines = content.split('\n')

        current_heading = None
        current_content = []

        for line in lines:
            match = self.heading_pattern.match(line)
            if match and len(match.group(1)) == 2:  # H2 heading
                # Save previous section
                if current_heading:
                    sections.append({
                        "heading": current_heading,
                        "content": '\n'.join(current_content).strip(),
                        "level": 2
                    })

                # Start new section
                current_heading = match.group(2).strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_heading:
            sections.append({
                "heading": current_heading,
                "content": '\n'.join(current_content).strip(),
                "level": 2
            })

        return sections

    def remove_frontmatter(self, content: str) -> str:
        """
        Remove YAML frontmatter from markdown

        Args:
            content: Markdown text with possible frontmatter

        Returns:
            Content without frontmatter
        """
        # Match frontmatter between --- delimiters
        frontmatter_pattern = re.compile(r'^---\s*\n.*?\n---\s*\n', re.DOTALL)
        cleaned = frontmatter_pattern.sub('', content, count=1)
        return cleaned.strip()


# Global parser instance
markdown_parser = MarkdownParser()
