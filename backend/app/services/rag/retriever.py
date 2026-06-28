"""
Hybrid Retrieval Pipeline:
  1. FAISS semantic search  (top-K*4 candidates)
  2. BM25 keyword search    (top-K*4 candidates)
  3. Score fusion           (RRF — Reciprocal Rank Fusion)
  4. Cross-encoder reranker (final top-K)

This prevents unrelated results (e.g. pollution act for FIR query)
by combining semantic meaning + exact keyword matching + reranking.
"""
from __future__ import annotations

import logging
import math
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple

from langchain.schema import Document

from app.core.config import get_settings

log = logging.getLogger(__name__)

_vectorstore   = None
_bm25_index    = None
_bm25_docs: List[Document] = []
_reranker      = None


# ── FAISS ────────────────────────────────────────────────────────────────────

def _load_vectorstore():
    global _vectorstore
    from langchain_community.vectorstores import FAISS
    from app.services.rag.embeddings import get_embeddings

    settings = get_settings()
    vs_path = settings.vectorstore_path

    if not vs_path.exists() or not (vs_path / "index.faiss").exists():
        raise FileNotFoundError(
            f"Vector database not found at '{vs_path}'. "
            "Run: python scripts/build_vectorstore.py"
        )

    embeddings = get_embeddings()
    _vectorstore = FAISS.load_local(
        str(vs_path), embeddings, allow_dangerous_deserialization=True
    )
    log.info("FAISS vectorstore loaded — %d vectors", _vectorstore.index.ntotal)
    return _vectorstore


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = _load_vectorstore()
    return _vectorstore


def reload_vectorstore() -> None:
    global _vectorstore, _bm25_index, _bm25_docs
    _vectorstore = None
    _bm25_index  = None
    _bm25_docs   = []
    get_vectorstore()
    _init_bm25()
    log.info("Vectorstore and BM25 index reloaded.")


def vectorstore_ready() -> bool:
    try:
        get_vectorstore()
        return True
    except Exception:
        return False


def get_document_count() -> int:
    try:
        return get_vectorstore().index.ntotal
    except Exception:
        return 0


def get_loaded_laws() -> List[str]:
    try:
        vs = get_vectorstore()
        acts = {
            doc.metadata.get("act_name", "")
            for doc in vs.docstore._dict.values()
            if hasattr(doc, "metadata")
        }
        return sorted(a for a in acts if a)
    except Exception:
        return []


# ── BM25 ─────────────────────────────────────────────────────────────────────

def _init_bm25():
    """Build BM25 index from all documents in the FAISS docstore."""
    global _bm25_index, _bm25_docs
    try:
        from rank_bm25 import BM25Okapi
        vs = get_vectorstore()
        _bm25_docs = list(vs.docstore._dict.values())
        tokenized = [
            (doc.page_content + " " + doc.metadata.get("act_name", "") +
             " " + doc.metadata.get("section", "")).lower().split()
            for doc in _bm25_docs
        ]
        _bm25_index = BM25Okapi(tokenized)
        log.info("BM25 index built — %d documents", len(_bm25_docs))
    except ImportError:
        log.warning("rank-bm25 not installed — BM25 hybrid search disabled. Run: pip install rank-bm25")
    except Exception as exc:
        log.warning("BM25 init failed: %s", exc)


def _bm25_search(query: str, k: int) -> List[Tuple[Document, float]]:
    """Return top-k BM25 results as (Document, score) tuples."""
    global _bm25_index, _bm25_docs
    if _bm25_index is None:
        _init_bm25()
    if _bm25_index is None:
        return []
    tokens = query.lower().split()
    scores = _bm25_index.get_scores(tokens)
    top_k_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    # Normalise BM25 score to [0, 1] range
    max_score = max(scores[i] for i in top_k_idx) if top_k_idx else 1.0
    if max_score == 0:
        return []
    return [
        (_bm25_docs[i], float(scores[i]) / max_score)
        for i in top_k_idx
        if scores[i] > 0
    ]


# ── Cross-Encoder Reranker ────────────────────────────────────────────────────

def _get_reranker():
    """Load cross-encoder reranker (lazy, cached)."""
    global _reranker
    if _reranker is not None:
        return _reranker
    try:
        from sentence_transformers import CrossEncoder
        # Lightweight, fast cross-encoder — good balance of quality vs speed
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
        log.info("Cross-encoder reranker loaded")
    except Exception as exc:
        log.warning("Reranker not available: %s — using RRF scores only", exc)
        _reranker = None
    return _reranker


def _rerank(query: str, candidates: List[Tuple[Document, float]], top_k: int) -> List[Tuple[Document, float]]:
    """Rerank candidate documents using a cross-encoder for precision."""
    reranker = _get_reranker()
    if reranker is None or len(candidates) <= top_k:
        return candidates[:top_k]

    try:
        pairs = [[query, doc.page_content[:512]] for doc, _ in candidates]
        scores = reranker.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return [item for (item, _) in ranked[:top_k]]
    except Exception as exc:
        log.warning("Reranking failed: %s", exc)
        return candidates[:top_k]


# ── Reciprocal Rank Fusion ────────────────────────────────────────────────────

def _rrf_fusion(
    faiss_results: List[Tuple[Document, float]],
    bm25_results:  List[Tuple[Document, float]],
    k_constant: int = 60,
) -> List[Tuple[Document, float]]:
    """
    Combine FAISS and BM25 results using Reciprocal Rank Fusion.
    RRF score = 1/(k + rank) — proven effective for hybrid retrieval.
    """
    scores: dict[str, float] = {}
    docs:   dict[str, Document] = {}

    def _doc_id(doc: Document) -> str:
        return f"{doc.metadata.get('act_name','')}::{doc.page_content[:80]}"

    for rank, (doc, _) in enumerate(faiss_results):
        did = _doc_id(doc)
        scores[did] = scores.get(did, 0) + 1.0 / (k_constant + rank + 1)
        docs[did] = doc

    for rank, (doc, _) in enumerate(bm25_results):
        did = _doc_id(doc)
        scores[did] = scores.get(did, 0) + 1.0 / (k_constant + rank + 1)
        docs[did] = doc

    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(docs[did], score) for did, score in fused]


# ── Similarity threshold filter ───────────────────────────────────────────────

def _filter_by_threshold(
    results: List[Tuple[Document, float]],
    query: str,
) -> List[Tuple[Document, float]]:
    """
    Remove results where the domain is obviously wrong.
    Uses the classifier as a sanity check on retrieved documents.
    """
    from app.services.nlp.classifier import classify_domain
    query_domain, query_conf = classify_domain(query)

    if query_conf < 0.3 or query_domain.value == "general":
        # Low-confidence query — don't filter, return all
        return results

    filtered = []
    for doc, score in results:
        doc_domain = doc.metadata.get("domain", "general")
        # Keep if domain matches OR if it's a general legal resource
        if doc_domain == query_domain.value or doc_domain == "general":
            filtered.append((doc, score))

    # Always return at least 2 results even if domain doesn't match
    return filtered if len(filtered) >= 2 else results


# ── Public retrieve function ──────────────────────────────────────────────────

def retrieve(
    query: str,
    k: int = 5,
    domain_filter: Optional[str] = None,
) -> List[Tuple[Document, float]]:
    """
    Hybrid retrieval: FAISS + BM25 → RRF fusion → domain filter → cross-encoder rerank.

    This pipeline prevents the 'pollution act for FIR query' problem by:
    1. Expanding candidates via both semantic (FAISS) and keyword (BM25) search
    2. Filtering results whose domain doesn't match the query
    3. Reranking with a cross-encoder for final precision
    """
    vs = get_vectorstore()

    if vs.index.ntotal == 0:
        raise RuntimeError(
            "No legal documents found in vector database. "
            "Run: python scripts/build_vectorstore.py"
        )

    fetch_k = min(k * 6, vs.index.ntotal)

    # 1. FAISS semantic search
    try:
        faiss_results = vs.similarity_search_with_score(query, k=fetch_k)
    except Exception as exc:
        log.error("FAISS search failed: %s", exc)
        faiss_results = []

    # 2. BM25 keyword search
    bm25_results = _bm25_search(query, k=fetch_k)

    # 3. RRF fusion
    if bm25_results:
        fused = _rrf_fusion(faiss_results, bm25_results)
    else:
        fused = faiss_results

    # 4. Domain-aware filtering (prevents pollution act for FIR queries)
    filtered = _filter_by_threshold(fused, query)

    # 5. Cross-encoder reranking for final precision
    reranked = _rerank(query, filtered, top_k=k)

    log.info(
        "Retrieval: FAISS=%d BM25=%d fused=%d filtered=%d final=%d",
        len(faiss_results), len(bm25_results), len(fused), len(filtered), len(reranked),
    )

    return reranked
