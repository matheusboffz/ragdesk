from fastapi.testclient import TestClient

from app.core.exceptions import AppError
from app.main import create_app


def test_health_endpoint_returns_ok() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/health", headers={"X-Request-ID": "test-req-123"})

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == "test-req-123"
    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "RAGDesk"
    assert "timestamp" in data


def test_standardized_app_error_handler() -> None:
    app = create_app()

    @app.get("/boom")
    def trigger_error() -> None:
        raise AppError(
            message="Custom domain failure",
            code="DOMAIN_FAILURE",
            status_code=400,
            details={"field": "sample"},
        )

    client = TestClient(app)
    response = client.get("/boom", headers={"X-Request-ID": "err-req-456"})

    assert response.status_code == 400
    payload = response.json()
    assert payload["error"]["code"] == "DOMAIN_FAILURE"
    assert payload["error"]["message"] == "Custom domain failure"
    assert payload["error"]["details"] == {"field": "sample"}
    assert payload["error"]["request_id"] == "err-req-456"

