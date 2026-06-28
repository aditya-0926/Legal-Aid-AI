"""
Centralised configuration with validation and helpful startup errors.
All settings are loaded from environment variables / .env file.
"""
from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingProvider(str, Enum):
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    BAAI_BGE = "baai_bge"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── App ──────────────────────────────────────────────────────────────
    APP_NAME: str = "Legal Aid AI"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ── Embedding ────────────────────────────────────────────────────────
    EMBEDDING_PROVIDER: EmbeddingProvider = EmbeddingProvider.SENTENCE_TRANSFORMERS
    EMBEDDING_MODEL_ST: str = "all-MiniLM-L6-v2"
    EMBEDDING_MODEL_BGE: str = "BAAI/bge-small-en-v1.5"

    # ── Groq LLM ─────────────────────────────────────────────────────────
# ── Groq LLM ─────────────────────────────────────────────────────────
    GROQ_API_KEY: Optional[str] = None
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    # ── Vector Store ─────────────────────────────────────────────────────
    VECTORSTORE_PATH: str = "data/vectorstore"
    DATA_RAW_PATH: str = "data/raw"
    DATA_PROCESSED_PATH: str = "data/processed"

    # ── RAG ──────────────────────────────────────────────────────────────
    RETRIEVAL_TOP_K: int = 5
    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 150

    # ── Upload ───────────────────────────────────────────────────────────
    MAX_UPLOAD_MB: int = 50
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [".pdf"]

    # ── Rate limiting ────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 30

    # ── CORS ─────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # ── Translation ──────────────────────────────────────────────────────
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = None

    # ── Validators ───────────────────────────────────────────────────────
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid:
            raise ValueError(f"LOG_LEVEL must be one of {valid}")
        return v.upper()

    @model_validator(mode="after")
    def warn_if_no_groq(self) -> "Settings":
        if not self.GROQ_API_KEY:
            print(
                "[CONFIG INFO] GROQ_API_KEY not set. "
                "The app will use rule-based fallback answers. "
                "Get a free key at https://console.groq.com",
                file=sys.stderr,
            )
        return self

    # ── Helpers ──────────────────────────────────────────────────────────
    @property
    def vectorstore_path(self) -> Path:
        return Path(self.VECTORSTORE_PATH)

    @property
    def raw_path(self) -> Path:
        return Path(self.DATA_RAW_PATH)

    @property
    def processed_path(self) -> Path:
        return Path(self.DATA_PROCESSED_PATH)

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_MB * 1024 * 1024


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
        print("LLM MODEL =", _settings.LLM_MODEL)
    return _settings
