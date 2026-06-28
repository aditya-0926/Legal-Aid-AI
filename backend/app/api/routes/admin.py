"""
Admin endpoints:
  - GET  /admin/status          → system status
  - GET  /admin/list-laws       → all indexed laws (built-in + uploaded)
  - GET  /admin/builtin-laws    → only built-in laws info
  - POST /admin/upload-law      → upload new PDF → auto-ingest
  - POST /admin/rebuild-vectorstore → rebuild full index
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import get_settings
from app.models.schemas import UploadResponse
from app.services.rag.builtin_loader import get_builtin_stats, list_builtin_laws
from app.services.rag.retriever import (
    get_document_count,
    get_loaded_laws,
    reload_vectorstore,
    vectorstore_ready,
)

log = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/status")
def admin_status():
    settings = get_settings()
    builtin = get_builtin_stats()
    raw_pdfs = (
        list((settings.raw_path / "pdfs").glob("*.pdf"))
        if (settings.raw_path / "pdfs").exists()
        else []
    )
    processed = (
        list(settings.processed_path.glob("*.json"))
        if settings.processed_path.exists()
        else []
    )
    return {
        "embedding_provider":    settings.EMBEDDING_PROVIDER.value,
        "llm_model":             settings.LLM_MODEL,
        "groq_configured":       bool(settings.GROQ_API_KEY),
        "chunk_size":            settings.CHUNK_SIZE,
        "chunk_overlap":         settings.CHUNK_OVERLAP,
        "retrieval_top_k":       settings.RETRIEVAL_TOP_K,
        "vectorstore_ready":     vectorstore_ready(),
        "total_vectors":         get_document_count(),
        "builtin_laws":          builtin["files"],
        "builtin_sections":      builtin["sections"],
        "uploaded_pdfs":         len(raw_pdfs),
        "processed_json_files":  len(processed),
    }


@router.get("/builtin-laws")
def builtin_laws():
    """List all laws that ship built-in with the application."""
    stats = get_builtin_stats()
    return {
        "description": "These laws are built-in and available immediately after deployment.",
        "total_laws":  stats["files"],
        "total_sections": stats["sections"],
        "laws": stats["laws"],
    }


@router.get("/list-laws")
def list_laws():
    """List all laws currently indexed (built-in + user uploaded)."""
    builtin_names = set(list_builtin_laws())
    all_loaded = get_loaded_laws()
    return {
        "total_indexed":  len(all_loaded),
        "vectorstore_ready": vectorstore_ready(),
        "document_count": get_document_count(),
        "laws": [
            {
                "act_name": name,
                "source": "built-in" if any(b in name.lower() for b in builtin_names) else "uploaded",
            }
            for name in all_loaded
        ],
    }


@router.post("/upload-law", response_model=UploadResponse)
async def upload_law(
    file: UploadFile = File(...),
    act_name: str = Form(..., min_length=3, max_length=200),
    domain: str = Form(default=""),
):
    """
    Upload a PDF bare act → auto-parse → chunk → add to FAISS index.
    The built-in laws remain untouched; this extends the knowledge base.
    No server restart required.
    """
    settings = get_settings()

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(400, f"Only PDF files are allowed. Got: '{suffix}'")

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            413, f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_MB} MB"
        )

    # Save to raw/pdfs/
    pdf_dir = settings.raw_path / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(
        c if c.isalnum() or c in "-_." else "_"
        for c in (file.filename or "upload.pdf")
    )
    pdf_path = pdf_dir / safe_name
    pdf_path.write_bytes(content)
    log.info("Saved upload: %s (%d bytes)", pdf_path, len(content))

    try:
        from app.services.admin.pdf_ingestion import ingest_pdf
        result = ingest_pdf(pdf_path, act_name, domain or None)

        if "error" in result:
            raise HTTPException(422, result["error"])

        return UploadResponse(
            filename=safe_name,
            sections_extracted=result["sections"],
            chunks_created=result["chunks"],
            message=(
                f"✅ '{act_name}' successfully added to the knowledge base. "
                f"It joins {get_builtin_stats()['files']} built-in laws already available."
            ),
        )
    except HTTPException:
        raise
    except Exception as exc:
        log.exception("Ingestion failed for %s", pdf_path)
        raise HTTPException(500, f"Ingestion failed: {exc}")


@router.post("/rebuild-vectorstore")
def rebuild_vectorstore():
    """
    Rebuild the entire FAISS index from scratch.
    Always includes built-in laws + all user-uploaded processed JSONs.
    """
    settings = get_settings()
    try:
        from app.services.rag.chunker import load_and_chunk
        from app.services.rag.embeddings import get_embeddings
        from langchain_community.vectorstores import FAISS

        log.info("Rebuilding vectorstore from built-in + uploaded laws...")
        docs = load_and_chunk(settings.processed_path)

        if not docs:
            raise HTTPException(
                422,
                "No documents found. This should not happen — "
                "check that app/data/builtin/ directory exists.",
            )

        embeddings = get_embeddings()
        vs_path = settings.vectorstore_path
        vs_path.mkdir(parents=True, exist_ok=True)
        vs = FAISS.from_documents(docs, embeddings)
        vs.save_local(str(vs_path))
        reload_vectorstore()

        builtin_stats = get_builtin_stats()
        return {
            "message":       "Vector store rebuilt successfully.",
            "total_chunks":  len(docs),
            "builtin_laws":  builtin_stats["files"],
            "total_vectors": vs.index.ntotal,
        }
    except HTTPException:
        raise
    except Exception as exc:
        log.exception("Rebuild failed")
        raise HTTPException(500, f"Rebuild failed: {exc}")
