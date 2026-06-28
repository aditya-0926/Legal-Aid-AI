"""
PDF text extraction using PyMuPDF (fitz) — no network calls, no scraping.
Falls back page-by-page to maximise text recovery from scanned / mixed PDFs.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Dict, Any

log = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    _FITZ_AVAILABLE = True
except ImportError:
    _FITZ_AVAILABLE = False
    log.warning("PyMuPDF (fitz) not installed. PDF parsing disabled. Run: pip install pymupdf")


def extract_pages(pdf_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extract text from every page of a PDF.
    Returns a list of dicts: {page_number, text}.
    """
    if not _FITZ_AVAILABLE:
        raise RuntimeError("PyMuPDF not installed. Run: pip install pymupdf")

    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    pages: List[Dict[str, Any]] = []
    try:
        doc = fitz.open(str(path))
        for i, page in enumerate(doc):
            text = page.get_text("text")
            if text.strip():
                pages.append({"page_number": i + 1, "text": text})
        doc.close()
    except Exception as exc:
        log.error("Failed to parse %s: %s", path.name, exc)
        raise RuntimeError(f"Could not parse PDF '{path.name}': {exc}") from exc

    log.info("Extracted %d pages from %s", len(pages), path.name)
    return pages


def pdf_to_text(pdf_path: str | Path) -> str:
    """Return full concatenated text from a PDF."""
    pages = extract_pages(pdf_path)
    return "\n\n".join(p["text"] for p in pages)
