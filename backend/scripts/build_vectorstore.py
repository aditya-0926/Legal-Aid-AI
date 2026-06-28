#!/usr/bin/env python3
"""
Build (or rebuild) the FAISS vector store.

Automatically includes:
  - All built-in Indian laws (shipped with the app)
  - Any user-uploaded laws from data/processed/

Usage:
    cd backend
    python scripts/build_vectorstore.py

Run this once after installation. The built-in knowledge base works
immediately — no PDF uploads required.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings
from app.core.logging import setup_logging

setup_logging("INFO")
log = logging.getLogger("build_vectorstore")


def main() -> None:
    settings = get_settings()

    log.info("=== Legal Aid AI — Build Vector Store ===")
    log.info("Embedding provider : %s", settings.EMBEDDING_PROVIDER.value)
    log.info("Output vectorstore : %s", settings.vectorstore_path)

    # Show built-in stats first
    from app.services.rag.builtin_loader import get_builtin_stats
    stats = get_builtin_stats()
    log.info("Built-in knowledge base: %d laws, %d sections", stats["files"], stats["sections"])
    for law in stats["laws"]:
        log.info("  ✓ %s (%d sections)", law["act"], law["sections"])

    # Load all documents (built-in + user uploaded)
    log.info("\nLoading and chunking all documents...")
    from app.services.rag.chunker import load_and_chunk
    docs = load_and_chunk(settings.processed_path)

    if not docs:
        log.error(
            "No documents produced. Check that app/data/builtin/ exists "
            "and contains JSON files."
        )
        sys.exit(1)

    log.info("Total chunks to index: %d", len(docs))

    # Load embedding model
    log.info("\nLoading embedding model (%s)...", settings.EMBEDDING_PROVIDER.value)
    log.info("(First run downloads ~90MB model — please wait)")
    try:
        from app.services.rag.embeddings import get_embeddings
        embeddings = get_embeddings()
    except Exception as exc:
        log.error("Failed to load embedding model: %s", exc)
        sys.exit(1)

    # Build FAISS index
    log.info("\nBuilding FAISS index...")
    try:
        from langchain_community.vectorstores import FAISS
        vs = FAISS.from_documents(docs, embeddings)
    except Exception as exc:
        log.error("FAISS indexing failed: %s", exc)
        sys.exit(1)

    # Save
    vs_path = settings.vectorstore_path
    vs_path.mkdir(parents=True, exist_ok=True)
    vs.save_local(str(vs_path))

    log.info("\n✅ Vector store saved to %s", vs_path)
    log.info("✅ Total vectors indexed: %d", vs.index.ntotal)
    log.info("\nStart the API: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
