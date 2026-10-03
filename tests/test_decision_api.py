from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_api_decision_source_gate():
    payload = {
        "question": "Should we query Gmail?",
        "state": {
            "prompt": "Write a follow-up email to Prof. Xavier Vance about our research",
            "task_type": "email_followup"
        },
        "options": ["yes", "no"]
    }
    res = client.post("/api/decision", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "yes"
    assert data["probability"] >= 0.85
    assert data["latency_ms"] < 20.0
    assert "probabilities" in data

def test_api_decision_sufficiency_gate():
    payload = {
        "question": "Is current evidence sufficient to generate?",
        "state": {
            "evidence_count": 9,
            "requirements_count": 5
        },
        "options": ["yes", "no"]
    }
    res = client.post("/api/decision", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "yes"
    assert data["probability"] >= 0.75
