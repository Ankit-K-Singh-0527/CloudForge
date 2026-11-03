
import pytest

from app import create_app
from app.config import ProductionConfig


@pytest.fixture
def app():
    return create_app("testing")


@pytest.fixture
def client(app):
    return app.test_client()


def test_development_configuration():
    app = create_app("development")

    assert app.config["DEBUG"] is True


def test_testing_configuration(app):
    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"] == "test-secret-key"


def test_production_requires_secret(monkeypatch):
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", None)

    with pytest.raises(RuntimeError, match="SECRET_KEY must be set"):
        create_app("production")


def test_invalid_configuration():
    with pytest.raises(ValueError, match="Invalid configuration"):
        create_app("invalid")


def test_health_endpoint(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"
    assert data["service"] == "CloudForge API"
