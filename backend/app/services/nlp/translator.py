"""
Translation service.
Uses Google Cloud Translate if key is configured, else returns text unchanged.
"""
from __future__ import annotations
import logging
from app.models.enums import Language

log = logging.getLogger(__name__)


def translate_text(text: str, target_lang: Language) -> str:
    if target_lang == Language.ENGLISH:
        return text
    from app.core.config import get_settings
    settings = get_settings()
    if not settings.GOOGLE_TRANSLATE_API_KEY:
        log.debug("GOOGLE_TRANSLATE_API_KEY not set — skipping translation")
        return text
    try:
        from google.cloud import translate_v2 as translate
        client = translate.Client()
        result = client.translate(text, target_language=target_lang.value)
        return result["translatedText"]
    except Exception as exc:
        log.warning("Translation failed: %s", exc)
        return text


def detect_language(text: str) -> str:
    from app.core.config import get_settings
    settings = get_settings()
    if not settings.GOOGLE_TRANSLATE_API_KEY:
        return "en"
    try:
        from google.cloud import translate_v2 as translate
        result = translate.Client().detect_language(text)
        return result["language"]
    except Exception:
        return "en"
