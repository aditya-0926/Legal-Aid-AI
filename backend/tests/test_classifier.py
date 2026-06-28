import pytest
from app.services.nlp.classifier import classify_domain
from app.models.enums import LegalDomain

@pytest.mark.parametrize("text,expected", [
    ("my landlord is not returning my rent deposit", LegalDomain.TENANT_RIGHTS),
    ("I want to file RTI for government information", LegalDomain.RTI),
    ("my husband beats me every day", LegalDomain.DOMESTIC_VIOLENCE),
    ("my employer fired me without notice and is not paying salary", LegalDomain.LABOR_LAW),
    ("I bought a defective product and they refuse refund", LegalDomain.CONSUMER_RIGHTS),
    ("my fundamental rights are violated by the government", LegalDomain.CONSTITUTION),
    ("I was in a car accident and want compensation", LegalDomain.MOTOR_VEHICLES),
    ("hello", LegalDomain.GENERAL),
])
def test_classify_domain(text, expected):
    domain, conf = classify_domain(text)
    assert domain == expected, f"Expected {expected.value}, got {domain.value}"
    if expected != LegalDomain.GENERAL:
        assert conf > 0

def test_confidence_bounds():
    _, conf = classify_domain("my landlord landlord landlord refuses deposit rent rent")
    assert 0 <= conf <= 1.0

def test_hindi_tenant():
    domain, _ = classify_domain("mera makaan kiraya wapas nahi mila")
    assert domain == LegalDomain.TENANT_RIGHTS
