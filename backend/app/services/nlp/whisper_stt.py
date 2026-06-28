"""
Speech-to-text using Groq's Whisper API (free).
Groq provides whisper-large-v3 for free — much faster than OpenAI's Whisper.
"""
from __future__ import annotations

import base64
import logging
import os
import tempfile

from app.core.config import get_settings

log = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


async def transcribe_audio(audio_base64: str, language: str = "hi") -> str:
    settings = get_settings()

    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is required for voice transcription. "
            "Get your free key at https://console.groq.com"
        )

    from openai import AsyncOpenAI

    # Groq Whisper endpoint — same SDK, different base_url and model
    client = AsyncOpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url=GROQ_BASE_URL,
    )

    audio_bytes = base64.b64decode(audio_base64)

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            transcript = await client.audio.transcriptions.create(
                model="whisper-large-v3",   # Free on Groq, faster than OpenAI
                file=f,
                language=language,
            )
        log.info("Transcribed audio (%s): %s chars", language, len(transcript.text))
        return transcript.text
    finally:
        os.unlink(tmp_path)
