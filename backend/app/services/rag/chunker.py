"""
Unified chunker: merges built-in laws + user-uploaded processed JSONs.

Priority:
  1. Built-in laws (shipped with app — always present)
  2. User-uploaded processed JSONs (from data/processed/)

Both are indexed into the same FAISS vectorstore.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import get_settings
from app.services.rag.builtin_loader import load_builtin_documents

log = logging.getLogger(__name__)


def _make_splitter() -> RecursiveCharacterTextSplitter:
    s = get_settings()
    return RecursiveCharacterTextSplitter(
        chunk_size=s.CHUNK_SIZE,
        chunk_overlap=s.CHUNK_OVERLAP,
        separators=["\n\n", "\n", "। ", ". ", " ", ""],
        length_function=len,
    )


def _load_user_uploaded(processed_dir: Path) -> List[Document]:
    """Load user-uploaded law JSONs from data/processed/."""
    splitter = _make_splitter()
    json_files = list(processed_dir.glob("*.json")) if processed_dir.exists() else []

    if not json_files:
        return []

    docs: List[Document] = []
    for jf in json_files:
        try:
            entries = json.loads(jf.read_text(encoding="utf-8"))
        except Exception as exc:
            log.error("Could not parse %s: %s", jf.name, exc)
            continue

        for entry in entries:
            text = entry.get("text", "").strip()
            if not text or len(text) < 30:
                continue

            metadata = {
                "act_name":    entry.get("act_name", "Unknown Act"),
                "section":     entry.get("section", ""),
                "chapter":     entry.get("chapter", ""),
                "domain":      entry.get("domain", "general"),
                "source_pdf":  entry.get("source_pdf", jf.name),
                "page_number": entry.get("page_number", 0),
                "is_builtin":  False,
            }
            docs.extend(splitter.create_documents([text], metadatas=[metadata]))

    log.info("User-uploaded laws: %d files → %d chunks", len(json_files), len(docs))
    return docs


def load_and_chunk(processed_dir: str | Path | None = None) -> List[Document]:
    """
    Load and chunk ALL documents:
      - Built-in laws (always included)
      - User-uploaded laws from processed_dir

    Returns a flat list of LangChain Documents ready for FAISS indexing.
    """
    settings = get_settings()
    base = Path(processed_dir) if processed_dir else settings.processed_path

    # 1. Built-in knowledge base
    log.info("Loading built-in knowledge base...")
    builtin_docs = load_builtin_documents()

    # 2. User-uploaded laws
    log.info("Loading user-uploaded laws from %s...", base)
    user_docs = _load_user_uploaded(base)

    all_docs = builtin_docs + user_docs

    log.info(
        "Total chunks: %d built-in + %d user-uploaded = %d",
        len(builtin_docs), len(user_docs), len(all_docs),
    )

    if not all_docs:
        log.warning(
            "No documents found at all! "
            "Built-in data directory may be missing. "
            "Check app/data/builtin/ directory exists."
        )

    return all_docs
