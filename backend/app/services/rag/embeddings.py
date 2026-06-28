"""
Embedding provider factory.
Default: all-mpnet-base-v2 — significantly better than all-MiniLM-L6-v2
for semantic search on legal text.
Switch via EMBEDDING_PROVIDER env var.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from app.core.config import EmbeddingProvider, get_settings

log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_embeddings() -> Any:
    settings = get_settings()
    provider = settings.EMBEDDING_PROVIDER

    if provider == EmbeddingProvider.BAAI_BGE:
        try:
            from langchain_community.embeddings import HuggingFaceBgeEmbeddings
            model = settings.EMBEDDING_MODEL_BGE
            log.info("Loading BAAI/BGE embeddings: %s", model)
            return HuggingFaceBgeEmbeddings(
                model_name=model,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        except ImportError as e:
            raise RuntimeError("Run: pip install sentence-transformers") from e

    # Default: SentenceTransformers
    try:
        from langchain_community.embeddings import SentenceTransformerEmbeddings
        # all-mpnet-base-v2: better quality than MiniLM for legal text
        # Falls back to MiniLM if user hasn't updated .env
        model = settings.EMBEDDING_MODEL_ST
        log.info("Loading SentenceTransformers: %s", model)
        return SentenceTransformerEmbeddings(model_name=model)
    except ImportError as e:
        raise RuntimeError("Run: pip install sentence-transformers") from e
