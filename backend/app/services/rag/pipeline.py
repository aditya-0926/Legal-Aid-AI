"""
RAG pipeline with:
- Query expansion (adds legal synonyms for better retrieval)
- Groq LLaMA-3 for natural answer generation
- Strict prompt that cites exact Act + Section in every answer
- Graceful fallback when no Groq key configured
"""
from __future__ import annotations

import logging
import re
import uuid
from typing import List, Optional

from app.core.config import get_settings
from app.models.enums import Language, LegalDomain
from app.models.schemas import ChatResponse, Citation, HistoryMessage, NearbyCenter
from app.services.nlp.classifier import classify_domain
from app.services.rag.retriever import retrieve

log = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"

LANGUAGE_NAMES = {
    Language.ENGLISH: "English",
    Language.HINDI:   "Hindi",
    Language.MARATHI: "Marathi",
}

# ── Query expansion dictionary ────────────────────────────────────────────────
# Maps short user queries to expanded legal terms for better retrieval
QUERY_EXPANSIONS = {
    "fir":              "FIR First Information Report cognizable offence police complaint BNSS Section 173",
    "bail":             "bail application bailable non-bailable offence BNSS magistrate custody",
    "arrest":           "arrest without warrant rights of arrested person BNSS Section 47 magistrate 24 hours",
    "divorce":          "divorce Hindu Marriage Act mutual consent cruelty desertion Section 13",
    "salary":           "salary wages unpaid employer Payment of Wages Act minimum wages retrenchment",
    "rent":             "rent landlord tenant deposit eviction Transfer of Property Act rental agreement",
    "rti":              "RTI Right to Information Act 2005 Section 6 public authority information",
    "consumer":         "consumer complaint defective product refund Consumer Protection Act district forum",
    "domestic violence":"domestic violence husband wife abuse protection order PWDVA 2005",
    "property":         "property land ownership deed registry boundary dispute succession",
    "cheque bounce":    "cheque bounce dishonour Negotiable Instruments Act Section 138 notice",
    "cyber":            "cybercrime IT Act hacking online fraud identity theft cybercrime.gov.in",
    "dowry":            "dowry prohibition harassment BNS Section 85 498A Dowry Prohibition Act",
    "epf":              "EPF provident fund withdrawal EPFO employee contribution employer",
    "maternity":        "maternity benefit leave Maternity Benefit Act 26 weeks employer",
}


def _expand_query(query: str) -> str:
    """Expand the user query with legal synonyms for better retrieval."""
    q_lower = query.lower()
    expansions = []
    for key, expansion in QUERY_EXPANSIONS.items():
        if key in q_lower:
            expansions.append(expansion)
    if expansions:
        return query + " " + " ".join(expansions)
    return query


# ── Context formatting ────────────────────────────────────────────────────────

def _format_context(docs_with_scores) -> str:
    parts = []
    for i, (doc, score) in enumerate(docs_with_scores, 1):
        m = doc.metadata
        relevance = round(max(0.0, 1.0 - float(score) / 2.0), 2) if isinstance(score, float) else 0.8
        header = (
            f"[Source {i}] {m.get('act_name', 'Unknown')} "
            f"— {m.get('section', '')} "
            f"(Page {m.get('page_number', '?')}, Relevance: {relevance:.0%})"
        )
        parts.append(f"{header}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def _build_citations(docs_with_scores) -> List[Citation]:
    return [
        Citation(
            act_name=      doc.metadata.get("act_name", "Unknown Act"),
            section=       doc.metadata.get("section", ""),
            chapter=       doc.metadata.get("chapter") or None,
            page_number=   doc.metadata.get("page_number") or None,
            source=        "built-in" if doc.metadata.get("is_builtin") else "uploaded",
            excerpt=       doc.page_content[:300],
            relevance_score=round(max(0.0, 1.0 - float(score) / 2.0), 3) if isinstance(score, float) else 0.8,
        )
        for doc, score in docs_with_scores
    ]


def _parse_sections(text: str):
    rights: List[str] = []
    steps:  List[str] = []

    rights_block = re.search(r"\*\*YOUR RIGHTS:\*\*(.*?)(?=\*\*|\Z)", text, re.S | re.I)
    if rights_block:
        for line in rights_block.group(1).splitlines():
            line = line.strip().lstrip("-•* 1234567890.")
            if len(line) > 10:
                rights.append(line)

    steps_block = re.search(r"\*\*NEXT STEPS:\*\*(.*?)(?=\*\*|\Z)", text, re.S | re.I)
    if steps_block:
        for line in steps_block.group(1).splitlines():
            line = re.sub(r"^\d+\.\s*", "", line.strip())
            if len(line) > 10:
                steps.append(line)

    return rights[:8], steps[:8]


# ── Groq system prompt ────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a knowledgeable Indian legal aid assistant helping low-income citizens understand their rights.

STRICT RULES:
1. Respond ONLY in {language_name}.
2. Base your answer EXCLUSIVELY on the Legal Context provided below. Do NOT use general knowledge.
3. Cite the EXACT Act name and Section number from the context in your answer.
4. ONLY cite sources that are directly relevant to the user's specific question.
5. Use plain, simple language — avoid legal jargon.
6. If the context does not contain relevant information for the specific question, say so clearly instead of guessing.
7. Keep answers focused and specific — do NOT add generic boilerplate about NALSA unless the context mentions it.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

**EXPLANATION:**
(2-3 sentences explaining the legal situation in plain language, citing which Act and Section applies)

**YOUR RIGHTS:**
- Right 1 (cite: Act Name, Section X)
- Right 2 (cite: Act Name, Section Y)

**NEXT STEPS:**
1. Specific immediate action
2. Who to contact and how
3. What documents to keep

**LEGAL BASIS:**
(List only the Acts/Sections from the context that are directly relevant to THIS question)

Legal Context:
{context}"""


# ── Main pipeline ─────────────────────────────────────────────────────────────

async def run_rag_pipeline(
    message:   str,
    language:  Language,
    history:   Optional[List[HistoryMessage]] = None,
    latitude:  Optional[float] = None,
    longitude: Optional[float] = None,
) -> ChatResponse:
    settings   = get_settings()
    session_id = str(uuid.uuid4())

    # 1. Classify domain
    domain, confidence = classify_domain(message)
    log.info("Query: '%s' → Domain: %s (%.0f%%)", message[:60], domain.value, confidence * 100)

    # 2. Expand query for better retrieval
    expanded_query = _expand_query(message)

    # 3. Hybrid retrieval (FAISS + BM25 + rerank)
    raw_docs  = retrieve(expanded_query, k=settings.RETRIEVAL_TOP_K, domain_filter=domain.value)
    context   = _format_context(raw_docs)
    citations = _build_citations(raw_docs)

    # 4. Generate answer
    if settings.GROQ_API_KEY:
        answer = await _generate_groq(message, context, language, history or [], settings)
        log.info("Groq answer generated (%d chars)", len(answer))
    else:
        answer = _generate_fallback(message, context, language, citations)
        log.info("Fallback answer generated (no GROQ_API_KEY)")

    # 5. Parse structured sections
    rights, steps = _parse_sections(answer)

    # 6. Nearby centers
    nearby: List[NearbyCenter] = []
    if latitude is not None and longitude is not None:
        try:
            from app.services.geo.nalsa_locator import find_nearby_centers
            nearby = find_nearby_centers(latitude, longitude)
        except Exception as exc:
            log.warning("Nearby centers failed: %s", exc)

    avg_relevance = (
        sum(c.relevance_score for c in citations) / len(citations) if citations else 0.0
    )

    return ChatResponse(
        session_id=        session_id,
        domain=            domain,
        domain_confidence= round(confidence, 2),
        answer=            answer,
        rights_summary=    rights,
        next_steps=        steps,
        citations=         citations,
        sources=           citations,
        nearby_centers=    nearby,
        language=          language,
        confidence=        round(avg_relevance, 2),
    )


async def _generate_groq(
    message:  str,
    context:  str,
    language: Language,
    history:  List[HistoryMessage],
    settings,
) -> str:
    from openai import AsyncOpenAI
    client    = AsyncOpenAI(api_key=settings.GROQ_API_KEY, base_url=GROQ_BASE_URL)
    lang_name = LANGUAGE_NAMES.get(language, "English")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(
            language_name=lang_name, context=context
        )}
    ]
    # Add last 6 history turns only
    for h in history[-6:]:
        content = h.content if h.role == "user" else (
            h.content if isinstance(h.content, str) else h.content.get("answer", "")
        )
        messages.append({"role": h.role, "content": str(content)[:800]})

    messages.append({"role": "user", "content": message})

    resp = await client.chat.completions.create(
        model=       settings.LLM_MODEL,
        messages=    messages,
        temperature= 0.1,   # Low temperature for factual legal answers
        max_tokens=  1500,
    )
    return resp.choices[0].message.content or ""


def _generate_fallback(
    message:   str,
    context:   str,
    language:  Language,
    citations: List[Citation],
) -> str:
    """Rule-based fallback — improved to show specific retrieved content."""
    lang_name = LANGUAGE_NAMES.get(language, "English")

    # Show top 2 most relevant retrieved passages
    top_context = context[:1000] if context else "No relevant legal provisions found."

    cite_lines = "\n".join(
        f"  • **{c.act_name}** — {c.section}"
        + (f" (Page {c.page_number})" if c.page_number else "")
        for c in citations[:3]
    ) or "  • No specific sections retrieved."

    return (
        f"**EXPLANATION:**\n"
        f"Based on the retrieved legal provisions, here is information relevant to your query:\n\n"
        f"{top_context}\n\n"
        f"**YOUR RIGHTS:**\n"
        f"- You have legal rights under the Indian laws cited below.\n"
        f"- You are entitled to free legal aid if you cannot afford a lawyer "
        f"(Legal Services Authorities Act 1987, Article 39A Constitution of India).\n\n"
        f"**NEXT STEPS:**\n"
        f"1. Call NALSA free helpline: **1800-11-0031** (24×7, toll-free).\n"
        f"2. Visit your nearest District Legal Services Authority (DLSA).\n"
        f"3. Bring all documents, agreements, and evidence related to your case.\n\n"
        f"**LEGAL BASIS:**\n{cite_lines}\n\n"
        f"---\n"
        f"*⚡ Add your free Groq API key to get precise, context-aware answers in {lang_name}.*\n"
        f"*Get it free at https://console.groq.com — takes 2 minutes.*"
    )
