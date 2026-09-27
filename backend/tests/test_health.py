from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "application": "ЦУТ Improvement Auto",
        "version": "0.1.0",
    }
