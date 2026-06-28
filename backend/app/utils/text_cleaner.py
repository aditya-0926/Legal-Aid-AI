"""
Utilities for cleaning raw text extracted from PDFs.
"""
from __future__ import annotations
import re


def clean_pdf_text(text: str) -> str:
    """Remove noise common in PDF-extracted text."""
    # Remove page headers/footers that appear as lone short lines
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip page numbers, lone digits, very short noise lines
        if re.fullmatch(r"\d{1,4}", stripped):
            continue
        if len(stripped) < 3 and stripped not in (".", ","):
            continue
        cleaned.append(line)
    text = "\n".join(cleaned)
    # Collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def normalize_section_title(title: str) -> str:
    """Normalise a section heading for consistent metadata."""
    title = re.sub(r"\s+", " ", title).strip()
    # Remove trailing punctuation
    title = title.rstrip(".-—")
    return title


def extract_section_number(title: str) -> str:
    """Extract the leading section number from a title string."""
    m = re.match(r"^(Section\s+\d+[\w.]*|Article\s+\d+[\w.]*|\d+[\w.]*)", title, re.I)
    return m.group(1) if m else ""
