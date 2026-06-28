"""Legal domain info and search endpoints."""
from fastapi import APIRouter, HTTPException
from app.models.enums import LegalDomain
from app.models.schemas import SearchRequest, SearchResult
from app.services.rag.retriever import retrieve, vectorstore_ready
import logging

log = logging.getLogger(__name__)
router = APIRouter(prefix="/legal", tags=["legal"])

DOMAIN_META = {
    LegalDomain.CONSTITUTION:        {"key_acts": ["Constitution of India 1950"]},
    LegalDomain.CRIMINAL_LAW:        {"key_acts": ["Bharatiya Nyaya Sanhita 2023 (BNS)"]},
    LegalDomain.CRIMINAL_PROCEDURE:  {"key_acts": ["Bharatiya Nagarik Suraksha Sanhita 2023 (BNSS)"]},
    LegalDomain.EVIDENCE:            {"key_acts": ["Bharatiya Sakshya Adhiniyam 2023 (BSA)"]},
    LegalDomain.TENANT_RIGHTS:       {"key_acts": ["Transfer of Property Act 1882", "Rent Control Acts (State-specific)"]},
    LegalDomain.LABOR_LAW:           {"key_acts": ["Industrial Disputes Act 1947", "Payment of Wages Act 1936", "EPF Act 1952"]},
    LegalDomain.DOMESTIC_VIOLENCE:   {"key_acts": ["PWDVA 2005", "IPC/BNS Section 498A"]},
    LegalDomain.RTI:                 {"key_acts": ["Right to Information Act 2005"]},
    LegalDomain.CONSUMER_RIGHTS:     {"key_acts": ["Consumer Protection Act 2019"]},
    LegalDomain.POLICE_MISCONDUCT:   {"key_acts": ["BNS", "BNSS", "Constitution Article 22"]},
    LegalDomain.PROPERTY_DISPUTE:    {"key_acts": ["Transfer of Property Act 1882", "Registration Act 1908"]},
    LegalDomain.FAMILY_LAW:          {"key_acts": ["Hindu Marriage Act 1955", "Special Marriage Act 1954"]},
    LegalDomain.MOTOR_VEHICLES:      {"key_acts": ["Motor Vehicles Act 1988"]},
    LegalDomain.IT_LAW:              {"key_acts": ["Information Technology Act 2000"]},
    LegalDomain.ENVIRONMENTAL:       {"key_acts": ["Environment Protection Act 1986", "NGT Act 2010"]},
    LegalDomain.GENERAL:             {"key_acts": []},
}


@router.get("/domains")
def list_domains():
    return [
        {"domain": d.value, "key_acts": DOMAIN_META.get(d, {}).get("key_acts", [])}
        for d in LegalDomain
    ]


@router.post("/search", response_model=list[SearchResult])
async def search(request: SearchRequest):
    if not vectorstore_ready():
        raise HTTPException(503, "Vector database not ready. Run build_vectorstore.py first.")
    try:
        results = retrieve(request.query, k=request.top_k, domain_filter=request.domain.value if request.domain else None)
        return [
            SearchResult(
                act_name=doc.metadata.get("act_name", ""),
                section=doc.metadata.get("section", ""),
                excerpt=doc.page_content[:300],
                relevance_score=round(max(0.0, 1.0 - float(score) / 2.0), 3),
                domain=doc.metadata.get("domain", "general"),
            )
            for doc, score in results
        ]
    except Exception as e:
        raise HTTPException(500, str(e))
