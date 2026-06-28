"""
Built-in knowledge base loader.

Loads all pre-packaged Indian law JSON files shipped with the application.
These are always available immediately after deployment — no PDF upload needed.

Users/admins can extend the knowledge base by uploading additional PDFs
via the /admin/upload-law endpoint, which merges into the same FAISS index.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import get_settings

log = logging.getLogger(__name__)


def _get_builtin_dir() -> Path:
    """
    Resolve the built-in data directory robustly.
    File lives at: backend/app/services/rag/builtin_loader.py
    Data lives at: backend/app/data/builtin/
    So we go: .parent (rag) → .parent (services) → .parent (app) → data/builtin
    """
    return Path(__file__).resolve().parent.parent.parent / "data" / "builtin"


def list_builtin_laws() -> List[str]:
    """Return the list of built-in law file stems."""
    builtin_dir = _get_builtin_dir()
    if not builtin_dir.exists():
        return []
    return sorted(f.stem for f in builtin_dir.glob("*.json"))


def load_builtin_documents() -> List[Document]:
    """
    Load all built-in law JSON files and chunk them into LangChain Documents.
    Called during vectorstore build so built-in laws are always indexed.
    """
    builtin_dir = _get_builtin_dir()

    if not builtin_dir.exists():
        log.warning("Built-in data directory not found: %s", builtin_dir)
        log.warning("Expected at: %s", builtin_dir)
        return []

    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", "। ", ". ", " ", ""],
    )

    json_files = list(builtin_dir.glob("*.json"))
    if not json_files:
        log.warning("No built-in JSON files found in %s", builtin_dir)
        return []

    all_docs: List[Document] = []
    for jf in sorted(json_files):
        try:
            entries = json.loads(jf.read_text(encoding="utf-8"))
        except Exception as exc:
            log.error("Could not parse built-in file %s: %s", jf.name, exc)
            continue

        file_docs = 0
        for entry in entries:
            text = entry.get("text", "").strip()
            if not text or len(text) < 30:
                continue

            metadata = {
                "act_name":    entry.get("act_name", "Unknown Act"),
                "section":     entry.get("section", ""),
                "chapter":     entry.get("chapter", ""),
                "domain":      entry.get("domain", "general"),
                "source_pdf":  entry.get("source_pdf", "builtin"),
                "page_number": entry.get("page_number", 0),
                "is_builtin":  True,
            }

            chunks = splitter.create_documents([text], metadatas=[metadata])
            all_docs.extend(chunks)
            file_docs += len(chunks)

        log.info("  ✓ %s → %d chunks", jf.name, file_docs)

    log.info(
        "Built-in knowledge base: %d files → %d total chunks",
        len(json_files),
        len(all_docs),
    )
    return all_docs


def get_builtin_stats() -> dict:
    """Return statistics about the built-in knowledge base."""
    builtin_dir = _get_builtin_dir()
    if not builtin_dir.exists():
        return {"files": 0, "sections": 0, "laws": [], "directory": str(builtin_dir)}

    total_sections = 0
    laws = []
    for jf in sorted(builtin_dir.glob("*.json")):
        try:
            entries = json.loads(jf.read_text(encoding="utf-8"))
            if entries:
                act_name = entries[0].get("act_name", jf.stem)
                laws.append({
                    "file":     jf.name,
                    "act":      act_name,
                    "sections": len(entries),
                })
                total_sections += len(entries)
        except Exception:
            pass

    return {
        "files":    len(laws),
        "sections": total_sections,
        "laws":     laws,
        "directory": str(builtin_dir),
    }
