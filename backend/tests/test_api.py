from unittest.mock import patch, AsyncMock
import pytest

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "vectorstore_ready" in data

def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Legal Aid AI" in r.json()["app"]

def test_list_domains(client):
    r = client.get("/legal/domains")
    assert r.status_code == 200
    domains = r.json()
    assert len(domains) >= 10
    domain_names = [d["domain"] for d in domains]
    assert "tenant_rights" in domain_names
    assert "rti" in domain_names
    assert "consumer_rights" in domain_names

def test_nearby_centers(client):
    r = client.get("/location/centers?lat=18.52&lon=73.85")
    assert r.status_code == 200
    centers = r.json()
    assert len(centers) > 0
    assert "name" in centers[0]
    assert "distance_km" in centers[0]

def test_chat_vectorstore_not_ready(client):
    r = client.post("/chat/", json={"message": "What are my tenant rights?"})
    # Should return 503, not 500
    assert r.status_code in (503, 200)

def test_search_not_ready(client):
    r = client.post("/legal/search", json={"query": "tenant rights"})
    assert r.status_code in (503, 200)
