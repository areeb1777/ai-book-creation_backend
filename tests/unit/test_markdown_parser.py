"""
Unit Tests for Markdown Parser

Tests heading extraction and hierarchy parsing.
"""

import pytest
from app.utils.markdown_parser import MarkdownParser


class TestMarkdownParser:
    """Test MarkdownParser class"""

    def test_extract_headings(self, sample_markdown):
        """Test heading extraction"""
        parser = MarkdownParser()
        headings = parser.extract_headings(sample_markdown)

        assert len(headings) > 0
        assert all('level' in h for h in headings)
        assert all('text' in h for h in headings)
        assert all('line_number' in h for h in headings)

        # Check H1 heading
        h1_headings = [h for h in headings if h['level'] == 1]
        assert len(h1_headings) >= 1
        assert "Chapter 1" in h1_headings[0]['text']

    def test_get_heading_hierarchy(self, sample_markdown):
        """Test heading hierarchy extraction"""
        parser = MarkdownParser()
        hierarchy = parser.get_heading_hierarchy(sample_markdown)

        assert 'h1' in hierarchy
        assert 'h2' in hierarchy
        assert 'h3' in hierarchy

        assert "Chapter 1" in hierarchy['h1']

    def test_extract_chapter_and_section(self, sample_markdown):
        """Test chapter and section extraction"""
        parser = MarkdownParser()
        chapter, section = parser.extract_chapter_and_section(sample_markdown)

        assert "Chapter 1" in chapter
        assert len(section) > 0

    def test_get_heading_path(self, sample_markdown):
        """Test heading path generation"""
        parser = MarkdownParser()
        path = parser.get_heading_path(sample_markdown)

        assert isinstance(path, list)
        assert len(path) >= 1
        assert "Chapter 1" in path[0]

    def test_remove_frontmatter(self):
        """Test frontmatter removal"""
        parser = MarkdownParser()
        markdown_with_frontmatter = """---
title: Test Page
description: Test description
---

# Chapter 1

Content here."""

        cleaned = parser.remove_frontmatter(markdown_with_frontmatter)

        assert "---" not in cleaned
        assert "title: Test Page" not in cleaned
        assert "# Chapter 1" in cleaned
        assert "Content here" in cleaned

    def test_split_by_headings(self, sample_markdown):
        """Test splitting by H2 headings"""
        parser = MarkdownParser()
        sections = parser.split_by_headings(sample_markdown)

        assert len(sections) > 0
        assert all('heading' in s for s in sections)
        assert all('content' in s for s in sections)
        assert all('level' in s for s in sections)
