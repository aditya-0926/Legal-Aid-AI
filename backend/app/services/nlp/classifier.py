"""
Legal domain classifier using keyword scoring.
Supports English, Hindi, and Marathi queries.
"""
from __future__ import annotations

import re
from typing import Tuple

from app.models.enums import LegalDomain

DOMAIN_KEYWORDS: dict[LegalDomain, list[str]] = {
    LegalDomain.CONSTITUTION: [
        "constitution", "fundamental right", "article", "directive principle",
        "equality", "freedom of speech", "right to life", "writ", "habeas corpus",
        "mandamus", "certiorari", "amendment", "संविधान", "मौलिक अधिकार",
        "basic right", "constitutional right", "supreme court writ",
    ],
    LegalDomain.CRIMINAL_PROCEDURE: [
        "arrested without warrant", "illegal arrest", "police custody", "bail application",
        "crpc", "bnss", "summons", "warrant", "chargesheet", "magistrate",
        "session court", "bail", "detained", "detention", "remand",
        "produced before magistrate", "custody", "arrested without",
        "समन", "वारंट", "मजिस्ट्रेट", "जमानत", "हिरासत",
    ],
    LegalDomain.CRIMINAL_LAW: [
        "murder", "theft", "robbery", "assault", "ipc", "bns", "bharatiya nyaya sanhita",
        "fir for", "file fir", "lodge fir", "offence", "crime", "accused",
        "cheating case", "fraud case", "hurt", "grievous hurt", "abetment",
        "criminal breach of trust", "stolen", "kidnap",
        "हत्या", "चोरी", "अपराध", "एफआईआर", "धोखाधड़ी",
    ],
    LegalDomain.EVIDENCE: [
        "evidence", "bsa", "sakshya", "witness", "document proof", "testimony",
        "confession", "admission", "burden of proof", "electronic evidence",
        "साक्ष्य", "गवाह", "सबूत",
    ],
    LegalDomain.TENANT_RIGHTS: [
        "rent", "landlord", "tenant", "eviction", "deposit", "lease", "flat",
        "house", "accommodation", "rental agreement", "notice to vacate",
        "security deposit", "vacate", "locked out",
        "किराया", "मकान मालिक", "किरायेदार", "बेदखली", "डिपॉझिट",
        "kiraya", "makaan", "evict",
    ],
    LegalDomain.LABOR_LAW: [
        "salary", "wages", "employer", "employee", "fired", "dismissed", "layoff",
        "pf", "provident fund", "esi", "gratuity", "overtime", "maternity leave",
        "minimum wage", "labour", "labor", "trade union", "strike", "retrenchment",
        "sexual harassment workplace", "termination", "job", "workplace",
        "वेतन", "नियोक्ता", "कर्मचारी", "नौकरी", "पीएफ", "श्रम",
        "naukri", "kaam",
    ],
    LegalDomain.DOMESTIC_VIOLENCE: [
        "domestic violence", "abuse", "beaten", "husband", "wife", "spouse",
        "harassment", "cruelty", "498a", "dowry", "protection order",
        "beats me", "hit me", "marital", "in laws",
        "घरेलू हिंसा", "पत्नी", "पति", "दहेज", "क्रूरता",
        "gharelu hinsa", "dahej",
    ],
    LegalDomain.RTI: [
        "rti", "right to information", "information from government", "government record",
        "public authority", "pio", "first appeal", "cic", "sic",
        "file rti", "get information from government",
        "सूचना का अधिकार", "जानकारी", "soochna",
    ],
    LegalDomain.CONSUMER_RIGHTS: [
        "consumer", "defective product", "refund", "service deficiency",
        "cheated by company", "online shopping fraud", "warranty", "misleading ad",
        "district forum", "consumer court", "defective phone", "defective goods",
        "उपभोक्ता", "धोखा", "वापसी", "वारंटी",
    ],
    LegalDomain.POLICE_MISCONDUCT: [
        "police brutality", "custodial death", "illegal detention", "false case",
        "bribe police", "encounter", "third degree", "police harass",
        "पुलिस", "अवैध हिरासत", "रिश्वत",
    ],
    LegalDomain.PROPERTY_DISPUTE: [
        "property", "land", "ownership", "deed", "registry", "boundary",
        "encroachment", "inheritance", "will", "mutation", "stamp duty",
        "zameen", "zamindari", "bhumi",
        "जमीन", "संपत्ति", "वसीयत", "उत्तराधिकार",
    ],
    LegalDomain.FAMILY_LAW: [
        "divorce", "custody", "maintenance", "alimony", "marriage",
        "separation", "adoption", "guardianship", "child support",
        "तलाक", "हिरासत", "गुजारा भत्ता", "शादी", "talaaq",
    ],
    LegalDomain.MOTOR_VEHICLES: [
        "accident", "motor vehicle", "car accident", "truck", "insurance claim",
        "hit and run", "driving licence", "traffic", "rto", "compensation accident",
        "road accident", "vehicle damage",
        "दुर्घटना", "वाहन", "बीमा", "मुआवजा",
    ],
    LegalDomain.IT_LAW: [
        "cyber", "hacking", "data breach", "online fraud", "it act",
        "digital", "social media", "identity theft", "phishing", "cybercrime",
        "साइबर", "डेटा चोरी", "ऑनलाइन धोखा",
    ],
    LegalDomain.ENVIRONMENTAL: [
        "pollution", "polluting", "environment", "forest", "wildlife",
        "ngt", "national green tribunal", "green tribunal",
        "waste disposal", "hazardous waste", "environmental damage",
        "air pollution", "water pollution", "noise pollution", "factory waste",
        "प्रदूषण", "पर्यावरण", "वन",
    ],
}


# Short single-word/phrase overrides for very short queries
_SHORT_OVERRIDES: dict[str, LegalDomain] = {
    "fir":            LegalDomain.CRIMINAL_PROCEDURE,
    "fir theft":       LegalDomain.CRIMINAL_LAW,
    "fir robbery":     LegalDomain.CRIMINAL_LAW,
    "fir murder":      LegalDomain.CRIMINAL_LAW,
    "fir fraud":       LegalDomain.CRIMINAL_LAW,
    "bail":           LegalDomain.CRIMINAL_PROCEDURE,
    "cheque bounce":  LegalDomain.CONSUMER_RIGHTS,
    "bounced cheque": LegalDomain.CONSUMER_RIGHTS,
    "dishonour":      LegalDomain.CONSUMER_RIGHTS,
    "rera":           LegalDomain.PROPERTY_DISPUTE,
    "epf":            LegalDomain.LABOR_LAW,
    "provident fund": LegalDomain.LABOR_LAW,
    "pf account":     LegalDomain.LABOR_LAW,
    "income tax":     LegalDomain.GENERAL,
    "gst":            LegalDomain.GENERAL,
    "pollution":      LegalDomain.ENVIRONMENTAL,
    "polluting":      LegalDomain.ENVIRONMENTAL,
}


def classify_domain(text: str) -> Tuple[LegalDomain, float]:
    """
    Score each domain by keyword frequency.
    Returns (domain, confidence) where confidence ∈ [0, 1].

    Two-pass approach:
    1. Short-phrase overrides for single-concept queries
    2. Full keyword scoring for multi-concept queries
    """
    normalized = text.lower()

    # Pass 1: short phrase overrides (catches "What is an FIR?", "cheque bounce" etc.)
    for phrase, domain in sorted(_SHORT_OVERRIDES.items(), key=lambda x: -len(x[0])):
        if phrase in normalized:
            return domain, 0.75

    # Pass 2: full keyword scoring
    scores: dict[LegalDomain, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        count = sum(1 for kw in keywords if re.search(re.escape(kw.lower()), normalized))
        if count:
            scores[domain] = count

    if not scores:
        return LegalDomain.GENERAL, 0.4

    best_domain = max(scores, key=scores.get)
    best_count  = scores[best_domain]
    confidence  = min(best_count / 3.0, 1.0)
    return best_domain, round(confidence, 2)
