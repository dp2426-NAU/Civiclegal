"""
CivicLegal AI — Health Endpoint Tests
"""
import os
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_returns_200():
    resp = client.get("/health")
    assert resp.status_code == 200


def test_health_has_required_fields():
    resp = client.get("/health")
    data = resp.json()
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert "disclaimer" in data


def test_health_status_is_healthy():
    resp = client.get("/health")
    data = resp.json()
    assert data["status"] == "healthy"


def test_health_includes_disclaimer():
    resp = client.get("/health")
    data = resp.json()
    disclaimer = data.get("disclaimer", "")
    assert "information" in disclaimer.lower() or "advice" in disclaimer.lower()


def test_legal_query_requires_question():
    resp = client.post("/legal-query", json={"question": "ab"})
    assert resp.status_code == 400


def test_legal_query_returns_demo_response():
    resp = client.post("/legal-query", json={"question": "What are my rights as a tenant?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "citations" in data
    assert "confidence" in data
    assert "disclaimer" in data


def test_legal_query_disclaimer_present():
    resp = client.post("/legal-query", json={"question": "What are my rights if I am arrested?"})
    assert resp.status_code == 200
    data = resp.json()
    disclaimer = data.get("disclaimer", "")
    assert len(disclaimer) > 20


def test_benefits_match_returns_programs():
    resp = client.post("/benefits-match", json={
        "household_size": 3,
        "annual_income": 28000,
        "state": "California",
        "has_children": True,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "programs" in data
    assert isinstance(data["programs"], list)


def test_benefits_match_disclaimer_present():
    resp = client.post("/benefits-match", json={
        "household_size": 1,
        "annual_income": 15000,
        "state": "Texas",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "disclaimer" in data
