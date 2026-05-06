from fastapi.testclient import TestClient
from src.app import create_app


def test_healthz_ok():
    app = create_app()
    client = TestClient(app)

    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
