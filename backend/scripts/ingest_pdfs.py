#!/usr/bin/env python3
"""
Batch-ingest all PDFs from data/raw/pdfs/ into structured JSON + FAISS.

Usage:
    cd backend
    python scripts/ingest_pdfs.py

The script reads a manifest file (data/raw/pdfs/manifest.json) to map each
PDF filename to its act name and domain. If no manifest exists, it falls back
to using the filename as the act name with auto-detected domain.

Manifest format (data/raw/pdfs/manifest.json):
[
  {"filename": "rti_act_2005.pdf", "act_name": "Right to Information Act 2005", "domain": "rti"},
  {"filename": "consumer_protection_2019.pdf", "act_name": "Consumer Protection Act 2019", "domain": "consumer_rights"}
]
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings
from app.core.logging import setup_logging

setup_logging("INFO")
log = logging.getLogger("ingest_pdfs")


def main() -> None:
    settings = get_settings()
    pdf_dir = settings.raw_path / "pdfs"

    log.info("=== Legal Aid AI — PDF Ingestion Pipeline ===")
    log.info("PDF directory: %s", pdf_dir)

    if not pdf_dir.exists():
        pdf_dir.mkdir(parents=True)
        log.error(
            "PDF directory '%s' did not exist (now created). "
            "Place your bare act PDFs there and re-run this script.",
            pdf_dir,
        )
        sys.exit(1)

    pdfs = list(pdf_dir.glob("*.pdf"))
    if not pdfs:
        log.error(
            "No PDF files found in '%s'.\n"
            "  Download Indian bare acts from https://indiacode.nic.in or https://legislative.gov.in\n"
            "  Place the PDFs in '%s' and re-run.",
            pdf_dir, pdf_dir,
        )
        _write_sample_manifest(pdf_dir)
        sys.exit(1)

    # Load manifest if available
    manifest_path = pdf_dir / "manifest.json"
    manifest: dict[str, dict] = {}
    if manifest_path.exists():
        try:
            entries = json.loads(manifest_path.read_text())
            manifest = {e["filename"]: e for e in entries}
            log.info("Loaded manifest with %d entries", len(manifest))
        except Exception as exc:
            log.warning("Could not parse manifest.json: %s — using filenames as act names", exc)

    from app.services.admin.pdf_ingestion import ingest_pdf

    success, failed = 0, 0
    for pdf in pdfs:
        meta = manifest.get(pdf.name, {})
        act_name = meta.get("act_name") or _filename_to_act_name(pdf.name)
        domain = meta.get("domain") or ""
        log.info("Ingesting: %s → '%s'", pdf.name, act_name)
        try:
            result = ingest_pdf(pdf, act_name, domain or None, save_json=True)
            if "error" in result:
                log.error("  ✗ %s", result["error"])
                failed += 1
            else:
                log.info("  ✓ %d sections, %d chunks", result["sections"], result["chunks"])
                success += 1
        except Exception as exc:
            log.exception("  ✗ Failed: %s", exc)
            failed += 1

    log.info("=== Done: %d succeeded, %d failed ===", success, failed)
    if success > 0:
        log.info("Run: python scripts/build_vectorstore.py  to (re)build the index")


def _filename_to_act_name(filename: str) -> str:
    name = Path(filename).stem
    name = name.replace("_", " ").replace("-", " ")
    return name.title()


def _write_sample_manifest(pdf_dir: Path) -> None:
    sample = [
        {"filename": "rti_act_2005.pdf", "act_name": "Right to Information Act 2005", "domain": "rti"},
        {"filename": "consumer_protection_2019.pdf", "act_name": "Consumer Protection Act 2019", "domain": "consumer_rights"},
        {"filename": "domestic_violence_act_2005.pdf", "act_name": "Protection of Women from Domestic Violence Act 2005", "domain": "domestic_violence"},
        {"filename": "bns_2023.pdf", "act_name": "Bharatiya Nyaya Sanhita 2023", "domain": "criminal_law"},
        {"filename": "bnss_2023.pdf", "act_name": "Bharatiya Nagarik Suraksha Sanhita 2023", "domain": "criminal_procedure"},
        {"filename": "bsa_2023.pdf", "act_name": "Bharatiya Sakshya Adhiniyam 2023", "domain": "evidence"},
        {"filename": "constitution_of_india.pdf", "act_name": "Constitution of India", "domain": "constitution"},
        {"filename": "motor_vehicles_act_1988.pdf", "act_name": "Motor Vehicles Act 1988", "domain": "motor_vehicles"},
        {"filename": "it_act_2000.pdf", "act_name": "Information Technology Act 2000", "domain": "it_law"},
        {"filename": "environment_protection_1986.pdf", "act_name": "Environment Protection Act 1986", "domain": "environmental"},
    ]
    out = pdf_dir / "manifest.json"
    out.write_text(json.dumps(sample, indent=2))
    log.info("Sample manifest written to %s — edit it to match your PDF filenames.", out)


if __name__ == "__main__":
    main()
