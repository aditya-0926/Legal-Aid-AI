import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

@pytest.fixture(scope="session")
def client():
    with patch("app.services.rag.retriever.get_vectorstore", side_effect=FileNotFoundError("test")):
        from app.main import app
        return TestClient(app, raise_server_exceptions=False)

@pytest.fixture
def mock_response():
    return MagicMock(
        session_id="test-123",
        domain=MagicMock(value="tenant_rights"),
        domain_confidence=0.85,
        answer="You have the right to receive your security deposit back.",
        rights_summary=["Right to deposit return"],
        next_steps=["Send demand letter"],
        sources=[],
        nearby_centers=[],
        language=MagicMock(value="en"),
        confidence=0.75,
    )
