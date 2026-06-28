"""
Admin service: ingest a PDF → parse → chunk → update FAISS index live.
No server restart required.
"""
from __future__ import annotations
import json, logging, re
from pathlib import Path
from typing import Optional

from app.core.config import get_settings
from app.models.enums import LegalDomain
from app.services.nlp.classifier import classify_domain
from app.utils.pdf_parser import extract_pages
from app.utils.text_cleaner import clean_pdf_text, normalize_section_title

log = logging.getLogger(__name__)

# Regex patterns for common section/article headings in Indian bare acts
_SECTION_RE = re.compile(
    r"^(Section\s+\d+[\w.-]*|Article\s+\d+[\w.-]*|\d+[\w.-]*\.)\s+(.+)$",
    re.MULTILINE | re.IGNORECASE,
)

_CHAPTER_RE = re.compile(r"^(Chapter\s+[IVXLC\d]+.*?)$", re.MULTILINE | re.IGNORECASE)


def _detect_domain(act_name: str, text: str) -> str:
    """Detect domain from act name first, fall back to keyword classifier."""
    name_lower = act_name.lower()
    mapping = {
        "domestic violence": LegalDomain.DOMESTIC_VIOLENCE.value,
        "right to information": LegalDomain.RTI.value,
        "consumer protection": LegalDomain.CONSUMER_RIGHTS.value,
        "labour": LegalDomain.LABOR_LAW.value,
        "motor vehicle": LegalDomain.MOTOR_VEHICLES.value,
        "information technology": LegalDomain.IT_LAW.value,
        "environment": LegalDomain.ENVIRONMENTAL.value,
        "bharatiya nyaya sanhita": LegalDomain.CRIMINAL_LAW.value,
        "bharatiya nagarik suraksha": LegalDomain.CRIMINAL_PROCEDURE.value,
        "bharatiya sakshya": LegalDomain.EVIDENCE.value,
        "constitution": LegalDomain.CONSTITUTION.value,
    }
    for kw, domain in mapping.items():
        if kw in name_lower:
            return domain
    domain, _ = classify_domain(text[:500])
    return domain.value


def parse_pdf_to_sections(
    pdf_path: Path,
    act_name: str,
    domain: Optional[str] = None,
) -> list[dict]:
    """
    Parse a PDF into structured section dicts ready for chunking.
    Returns list of {act_name, section, chapter, text, domain, source_pdf, page_number}.
    """
    pages = extract_pages(pdf_path)
    full_text = "\n\n".join(clean_pdf_text(p["text"]) for p in pages)

    detected_domain = domain or _detect_domain(act_name, full_text)

    # Split by section headings; fall back to page-level chunks
    sections = []
    chapter = ""
    last_end = 0

    chapter_matches = list(_CHAPTER_RE.finditer(full_text))
    section_matches = list(_SECTION_RE.finditer(full_text))

    if len(section_matches) >= 3:
        # Section-aware splitting
        chapter_idx = 0
        for i, m in enumerate(section_matches):
            # Update current chapter
            while chapter_idx < len(chapter_matches) and chapter_matches[chapter_idx].start() < m.start():
                chapter = normalize_section_title(chapter_matches[chapter_idx].group(1))
                chapter_idx += 1

            start = m.start()
            end = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(full_text)
            body = full_text[start:end].strip()

            # Estimate page number
            char_count = sum(len(p["text"]) for p in pages)
            page_approx = max(1, round(start / max(char_count, 1) * len(pages)))

            sections.append({
                "act_name": act_name,
                "section": normalize_section_title(m.group(0)[:120]),
                "chapter": chapter,
                "text": body,
                "domain": detected_domain,
                "source_pdf": pdf_path.name,
                "page_number": page_approx,
            })
    else:
        # Fallback: page-level chunks
        for p in pages:
            text = clean_pdf_text(p["text"])
            if len(text) > 100:
                sections.append({
                    "act_name": act_name,
                    "section": f"Page {p['page_number']}",
                    "chapter": "",
                    "text": text,
                    "domain": detected_domain,
                    "source_pdf": pdf_path.name,
                    "page_number": p["page_number"],
                })

    log.info("Parsed %d sections from %s", len(sections), pdf_path.name)
    return sections


def ingest_pdf(
    pdf_path: Path,
    act_name: str,
    domain: Optional[str] = None,
    save_json: bool = True,
) -> dict:
    """
    Full ingestion pipeline for one PDF:
    parse → save JSON → chunk → add to FAISS → reload retriever.
    Returns summary dict.
    """
    settings = get_settings()

    sections = parse_pdf_to_sections(pdf_path, act_name, domain)
    if not sections:
        return {"sections": 0, "chunks": 0, "error": "No text extracted from PDF"}

    if save_json:
        out_dir = settings.processed_path
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^\w\-]", "_", act_name.lower())[:60]
        out_file = out_dir / f"{safe_name}.json"
        out_file.write_text(json.dumps(sections, ensure_ascii=False, indent=2), encoding="utf-8")
        log.info("Saved %d sections → %s", len(sections), out_file)

    # Rebuild (or update) the vector store
    from app.services.rag.chunker import load_and_chunk
    from app.services.rag.embeddings import get_embeddings
    from app.services.rag.retriever import reload_vectorstore
    from langchain_community.vectorstores import FAISS

    docs = load_and_chunk(settings.processed_path)
    if not docs:
        return {"sections": len(sections), "chunks": 0, "error": "Chunking produced no documents"}

    embeddings = get_embeddings()
    vs_path = settings.vectorstore_path
    vs_path.mkdir(parents=True, exist_ok=True)

    if (vs_path / "index.faiss").exists():
        vs = FAISS.load_local(str(vs_path), embeddings, allow_dangerous_deserialization=True)
        # Add only new docs to existing index
        new_docs = load_and_chunk(out_dir if save_json else settings.processed_path)
        vs.add_documents(new_docs)
    else:
        vs = FAISS.from_documents(docs, embeddings)

    vs.save_local(str(vs_path))
    reload_vectorstore()

    log.info("Vector store updated: %d total vectors", vs.index.ntotal)
    return {"sections": len(sections), "chunks": len(docs)}
