"""
Legal Aid AI — FastAPI application entry point.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.api.routes import chat, health, legal, location, admin

settings = get_settings()
setup_logging(settings.LOG_LEVEL)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: pre-warm embeddings and try to load vectorstore."""
    log.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    try:
        from app.services.rag.embeddings import get_embeddings
        get_embeddings()
        log.info("Embedding model loaded (%s)", settings.EMBEDDING_PROVIDER.value)
    except Exception as exc:
        log.warning("Embedding model not loaded at startup: %s", exc)

    try:
        from app.services.rag.retriever import get_vectorstore
        vs = get_vectorstore()
        log.info("Vector store ready — %d vectors", vs.index.ntotal)
    except FileNotFoundError:
        log.warning(
            "Vector store not found. Run: python scripts/build_vectorstore.py "
            "or upload PDFs via POST /admin/upload-law"
        )
    except Exception as exc:
        log.warning("Vector store could not be loaded: %s", exc)

    yield
    log.info("Shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RAG-powered multilingual legal aid assistant for Indian citizens",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

# ── Global exception handlers ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(legal.router)
app.include_router(location.router)
app.include_router(admin.router)


@app.get("/", tags=["root"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
