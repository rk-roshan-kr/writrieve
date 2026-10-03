from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "Qwen3" in data["model_architecture"]
    assert data["indexed_signals"] == 200

def test_api_benchmark():
    res = client.get("/api/benchmark")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3
    # Check that Write4U uses lowest token count and 0 noise
    w4u = [r for r in data if "Write4U" in r["system"]][0]
    normal = [r for r in data if "Normal Agent" in r["system"]][0]
    assert w4u["tokens_used"] < normal["tokens_used"]
    assert w4u["irrelevant_context_rate"] == 0.0

def test_api_generate():
    payload = {
        "prompt": "Write a follow-up email to the professor I met at the conference about continuing our research.",
        "page_context": {
            "site": "gmail",
            "recipient": "Prof. Xavier Vance <xvance@csail.mit.edu>",
            "subject": "Re: Continuing FieldChain Research"
        }
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "draft" in data
    assert len(data["draft"]) > 100
    assert data["funnel"]["candidates"] == 200
    assert data["funnel"]["selected"] == len(data["selected_evidence"])
    assert len(data["claims_provenance"]) > 0
