"""Pydantic v2 request / response models."""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from .enums import LegalDomain, Language


# ── Request models ────────────────────────────────────────────────────────────

class HistoryMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=3, max_length=2000)
    language: Language = Language.ENGLISH
    session_id: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    history: List[HistoryMessage] = Field(default_factory=list, max_length=20)

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        return v.strip()

class TranscribeRequest(BaseModel):
    audio_base64: str
    language: Language = Language.HINDI

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    domain: Optional[LegalDomain] = None
    top_k: int = Field(5, ge=1, le=20)


# ── Response models ───────────────────────────────────────────────────────────

class Citation(BaseModel):
    """Full citation with act name, section, chapter and page — shown with every answer."""
    act_name: str
    section: str
    chapter: Optional[str] = None
    page_number: Optional[int] = None
    source: str = "builtin"          # "builtin" or "uploaded"
    excerpt: str
    relevance_score: float

# Keep LegalSource as alias so existing code doesn't break
LegalSource = Citation

class NearbyCenter(BaseModel):
    name: str
    address: str
    phone: str
    distance_km: float

class ChatResponse(BaseModel):
    session_id: str
    domain: LegalDomain
    domain_confidence: float
    answer: str
    rights_summary: List[str]
    next_steps: List[str]
    citations: List[Citation]           # renamed from sources
    sources: List[Citation]             # kept for backward compat
    nearby_centers: List[NearbyCenter]
    language: Language
    confidence: float = Field(0.0, ge=0, le=1)

class StatusResponse(BaseModel):
    status: str
    version: str
    vectorstore_ready: bool
    document_count: int
    embedding_provider: str
    laws_loaded: List[str]
    builtin_laws: int = 0
    groq_configured: bool = False

class UploadResponse(BaseModel):
    filename: str
    sections_extracted: int
    chunks_created: int
    message: str

class SearchResult(BaseModel):
    act_name: str
    section: str
    chapter: Optional[str] = None
    page_number: Optional[int] = None
    excerpt: str
    relevance_score: float
    domain: str
    source: str = "builtin"

ChatRequest.model_rebuild()
