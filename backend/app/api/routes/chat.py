"""Chat and transcription endpoints."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, TranscribeRequest
from app.services.rag.pipeline import run_rag_pipeline
from app.services.nlp.whisper_stt import transcribe_audio
import logging

log = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        return await run_rag_pipeline(
            message=request.message,
            language=request.language,
            history=request.history,
            latitude=request.latitude,
            longitude=request.longitude,
        )
    except FileNotFoundError as e:
        raise HTTPException(503, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(503, detail=str(e))
    except Exception as e:
        log.exception("Unexpected error in /chat")
        raise HTTPException(500, detail="An unexpected error occurred. Please try again.")


@router.post("/transcribe")
async def transcribe(request: TranscribeRequest):
    try:
        text = await transcribe_audio(request.audio_base64, request.language.value)
        return {"text": text, "language": request.language}
    except RuntimeError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        log.exception("Transcription failed")
        raise HTTPException(500, detail="Transcription failed.")
