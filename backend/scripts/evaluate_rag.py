#!/usr/bin/env python3
"""
Evaluate the RAG pipeline on a ground-truth QA dataset.

Metrics:
  - Domain classification accuracy (no vectorstore needed)
  - Retrieval relevance@k (requires vectorstore to be built)
  - Query expansion coverage

Usage:
    cd backend
    python scripts/evaluate_rag.py
"""
from __future__ import annotations
import sys, logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.core.logging import setup_logging

setup_logging("INFO")
log = logging.getLogger("evaluate_rag")

# Ground truth: query → expected domain + expected keyword in top-k results
EVAL_DATASET = [
    {
        "query":   "What is an FIR?",
        "domain":  "criminal_procedure",
        "must_contain": ["first information report", "fir", "bnss", "cognizable"],
    },
    {
        "query":   "My landlord is not returning my security deposit",
        "domain":  "tenant_rights",
        "must_contain": ["deposit", "landlord", "tenant", "rent"],
    },
    {
        "query":   "My employer has not paid salary for 3 months",
        "domain":  "labor_law",
        "must_contain": ["wages", "salary", "payment", "employer"],
    },
    {
        "query":   "How to file RTI application",
        "domain":  "rti",
        "must_contain": ["right to information", "rti", "public information officer"],
    },
    {
        "query":   "My husband beats me every day",
        "domain":  "domestic_violence",
        "must_contain": ["domestic violence", "protection", "cruelty"],
    },
    {
        "query":   "I bought defective phone company refuses refund",
        "domain":  "consumer_rights",
        "must_contain": ["consumer", "defect", "refund", "complaint"],
    },
    {
        "query":   "Police arrested me without warrant",
        "domain":  "criminal_procedure",
        "must_contain": ["arrest", "warrant", "magistrate", "24 hours"],
    },
    {
        "query":   "Car accident highway insurance compensation",
        "domain":  "motor_vehicles",
        "must_contain": ["accident", "compensation", "insurance", "motor vehicle"],
    },
    {
        "query":   "Someone hacked my bank account online fraud",
        "domain":  "it_law",
        "must_contain": ["cyber", "fraud", "it act", "cybercrime"],
    },
    {
        "query":   "Factory near my house causing pollution",
        "domain":  "environmental",
        "must_contain": ["pollution", "environment", "ngt", "tribunal"],
    },
    {
        "query":   "Cheque bounce what can I do",
        "domain":  "consumer_rights",
        "must_contain": ["cheque", "dishonour", "negotiable instruments"],
    },
    {
        "query":   "My EPF provident fund employer not depositing",
        "domain":  "labor_law",
        "must_contain": ["epf", "provident fund", "employer", "contribution"],
    },
]


def evaluate_classifier():
    from app.services.nlp.classifier import classify_domain
    log.info("── Domain Classifier ─────────────────────────────────────")
    correct = 0
    for s in EVAL_DATASET:
        domain, conf = classify_domain(s["query"])
        ok = domain.value == s["domain"]
        correct += ok
        mark = "✅" if ok else "❌"
        log.info("%s %-22s → %-22s (%.0f%%)", mark, s["domain"], domain.value, conf * 100)
    acc = correct / len(EVAL_DATASET)
    log.info("Classifier: %d/%d = %.0f%%\n", correct, len(EVAL_DATASET), acc * 100)
    return acc


def evaluate_retrieval():
    from app.services.rag.retriever import vectorstore_ready, retrieve
    from app.services.rag.pipeline import _expand_query

    log.info("── Retrieval Quality (with query expansion + reranking) ───")
    if not vectorstore_ready():
        log.warning("Vector store not ready. Run: python scripts/build_vectorstore.py")
        return None

    hits, total = 0, 0
    for s in EVAL_DATASET:
        expanded = _expand_query(s["query"])
        try:
            results = retrieve(expanded, k=5)
            combined_text = " ".join(
                (doc.metadata.get("act_name", "") + " " + doc.page_content).lower()
                for doc, _ in results
            )
            # Check if any required keyword appears in results
            matched = any(kw.lower() in combined_text for kw in s["must_contain"])
            hits += matched
            total += 1

            top_act = results[0][0].metadata.get("act_name", "?") if results else "no results"
            mark = "✅" if matched else "❌"
            log.info("%s %-45s → %s", mark, s["query"][:44], top_act[:45])
        except Exception as exc:
            log.warning("Retrieval error for '%s': %s", s["query"][:40], exc)

    if total == 0:
        return None
    recall = hits / total
    log.info("Retrieval relevance@5: %d/%d = %.0f%%\n", hits, total, recall * 100)
    return recall


def evaluate_query_expansion():
    from app.services.rag.pipeline import _expand_query
    log.info("── Query Expansion Coverage ──────────────────────────────")
    expanded_count = 0
    for s in EVAL_DATASET:
        expanded = _expand_query(s["query"])
        if len(expanded) > len(s["query"]):
            expanded_count += 1
            log.info("  ✅ '%s'", s["query"][:50])
        else:
            log.info("  ○  '%s' (no expansion)", s["query"][:50])
    log.info("Expanded %d/%d queries\n", expanded_count, len(EVAL_DATASET))


if __name__ == "__main__":
    evaluate_query_expansion()
    classifier_acc   = evaluate_classifier()
    retrieval_recall = evaluate_retrieval()

    log.info("═══════════════════════════════════════════════════════")
    log.info("SUMMARY")
    log.info("  Classifier accuracy  : %.0f%%", classifier_acc * 100)
    if retrieval_recall is not None:
        log.info("  Retrieval recall@5   : %.0f%%", retrieval_recall * 100)
    else:
        log.info("  Retrieval recall@5   : N/A (build vectorstore first)")
    log.info("═══════════════════════════════════════════════════════")
