from fastapi.testclient import TestClient

from apps.api.main import app


def test_health_endpoint_contract() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert {"environment", "payer", "market", "line_of_business"} <= payload.keys()
