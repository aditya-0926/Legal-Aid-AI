from fastapi import APIRouter
from app.core.config import get_settings
from app.models.schemas import StatusResponse
from app.services.rag.retriever import vectorstore_ready, get_document_count, get_loaded_laws
from app.services.rag.builtin_loader import get_builtin_stats

router = APIRouter(tags=["health"])


@router.get("/health", response_model=StatusResponse)
def health_check():
    settings = get_settings()
    builtin = get_builtin_stats()
    return StatusResponse(
        status="ok",
        version=settings.APP_VERSION,
        vectorstore_ready=vectorstore_ready(),
        document_count=get_document_count(),
        embedding_provider=settings.EMBEDDING_PROVIDER.value,
        laws_loaded=get_loaded_laws(),
        builtin_laws=builtin["files"],
        groq_configured=bool(settings.GROQ_API_KEY),
    )
