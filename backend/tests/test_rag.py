import json, pytest
from pathlib import Path
from app.services.rag.chunker import load_and_chunk

def test_chunker_empty_dir(tmp_path):
    docs = load_and_chunk(tmp_path)
    assert docs == []

def test_chunker_with_valid_data(tmp_path):
    sample = [{
        "act_name": "Test Act 2024",
        "section": "Section 1 — Definitions",
        "chapter": "Chapter I",
        "text": "This is a test section with enough content. " * 30,
        "domain": "general",
        "source_pdf": "test.pdf",
        "page_number": 1,
    }]
    (tmp_path / "test.json").write_text(json.dumps(sample))
    docs = load_and_chunk(tmp_path)
    assert len(docs) >= 1
    assert docs[0].metadata["act_name"] == "Test Act 2024"
    assert docs[0].metadata["domain"] == "general"
    assert "section" in docs[0].metadata

def test_chunker_skips_short_text(tmp_path):
    sample = [{"act_name": "A", "section": "S1", "text": "Too short", "domain": "general"}]
    (tmp_path / "a.json").write_text(json.dumps(sample))
    docs = load_and_chunk(tmp_path)
    assert docs == []

def test_chunker_skips_malformed_json(tmp_path):
    (tmp_path / "bad.json").write_text("{not valid json")
    docs = load_and_chunk(tmp_path)
    assert docs == []

def test_geo_built_in():
    from app.services.geo.nalsa_locator import find_nearby_centers
    results = find_nearby_centers(18.52, 73.85)
    assert len(results) > 0
    assert results[0].distance_km < results[-1].distance_km  # sorted
    assert results[0].phone
