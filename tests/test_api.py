from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_diagnose_endpoint_full_match() -> None:
    payload = {"selected": ["JG01", "JG02", "JG03", "JG04"]}
    response = client.post("/api/diagnose", params={"strict": "true"}, json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["diagnoses"], "Expected diagnoses"
    first = body["diagnoses"][0]
    assert first["disease"]["code"] == "P1"
    assert first["missing"] == []
    assert body["message"] is None


def test_diagnose_endpoint_invalid_code() -> None:
    response = client.post("/api/diagnose", json={"selected": ["UNKNOWN"]})
    assert response.status_code == 422
    body = response.json()
    assert body["detail"]["error"] == "Kode gejala tidak dikenal"
    assert "UNKNOWN" in body["detail"]["invalid"]


def test_diagnose_partial_mode_returns_candidates() -> None:
    response = client.post("/api/diagnose", json={"selected": ["JG01"]})
    assert response.status_code == 200
    body = response.json()
    assert body["diagnoses"], "Expected partial candidates"
    assert body["message"] == "Tidak diketahui"
    assert any(entry["missing"] for entry in body["diagnoses"])