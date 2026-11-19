
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.middleware import require_auth, require_csrf


@pytest.fixture
def middleware_client(app, monkeypatch):
    """Create temporary routes protected by authentication middleware."""

    user = SimpleNamespace(
        id="test-user-id",
        email="test@example.com",
    )

    user_session = SimpleNamespace(user=user)

    validate_session = Mock(return_value=user_session)
    validate_csrf = Mock(return_value=True)

    monkeypatch.setattr(
        "app.middleware.validate_session",
        validate_session,
    )

    monkeypatch.setattr(
        "app.middleware.validate_csrf_token",
        validate_csrf,
    )

    @app.get("/middleware-test/protected")
    @require_auth
    def protected_route():
        from flask import g, jsonify

        return jsonify({
            "user_id": g.current_user.id,
            "authenticated": True,
        }), 200

    @app.post("/middleware-test/action")
    @require_auth
    @require_csrf
    def protected_action():
        return {"message": "Action completed."}, 200

    return {
        "client": app.test_client(),
        "user_session": user_session,
        "validate_session": validate_session,
        "validate_csrf": validate_csrf,
    }


def set_valid_session_cookie(client):
    """Simulate a browser sending a valid session cookie."""

    client.set_cookie(
        "cloudforge_session",
        "valid-token",
    )


def test_missing_session_cookie_returns_401(middleware_client):
    response = middleware_client["client"].get(
        "/middleware-test/protected"
    )

    assert response.status_code == 401
    assert response.json["error"] == "Authentication required."

    middleware_client["validate_session"].assert_not_called()


def test_invalid_session_returns_401(middleware_client):
    middleware_client["validate_session"].return_value = None

    client = middleware_client["client"]
    set_valid_session_cookie(client)

    response = client.get("/middleware-test/protected")

    assert response.status_code == 401
    assert response.json["error"] == "Authentication required."

    middleware_client["validate_session"].assert_called_once_with(
        "valid-token"
    )


def test_valid_session_allows_protected_request(middleware_client):
    client = middleware_client["client"]
    set_valid_session_cookie(client)

    response = client.get("/middleware-test/protected")

    assert response.status_code == 200
    assert response.json["authenticated"] is True
    assert response.json["user_id"] == "test-user-id"

    middleware_client["validate_session"].assert_called_once_with(
        "valid-token"
    )


def test_missing_origin_returns_403(middleware_client):
    client = middleware_client["client"]
    set_valid_session_cookie(client)

    response = client.post(
        "/middleware-test/action",
        headers={
            "X-CSRF-Token": "valid-csrf-token",
        },
    )

    assert response.status_code == 403
    assert response.json["error"] == "Untrusted request origin."

    middleware_client["validate_session"].assert_called_once_with(
        "valid-token"
    )


def test_untrusted_origin_returns_403(middleware_client):
    client = middleware_client["client"]
    set_valid_session_cookie(client)

    response = client.post(
        "/middleware-test/action",
        headers={
            "Origin": "https://untrusted.example",
            "X-CSRF-Token": "valid-csrf-token",
        },
    )

    assert response.status_code == 403
    assert response.json["error"] == "Untrusted request origin."


def test_missing_csrf_token_returns_403(middleware_client):
    client = middleware_client["client"]
    set_valid_session_cookie(client)

    response = client.post(
        "/middleware-test/action",
        headers={
            "Origin": "http://localhost:5173",
        },
    )

    assert response.status_code == 403
    assert response.json["error"] == "CSRF token is required."


def test_invalid_csrf_token_returns_403(middleware_client):
    middleware_client["validate_csrf"].return_value = False

    client = middleware_client["client"]
    set_valid_session_cookie(client)

    response = client.post(
        "/middleware-test/action",
        headers={
            "Origin": "http://localhost:5173",
            "X-CSRF-Token": "invalid-csrf-token",
        },
    )

    assert response.status_code == 403
    assert response.json["error"] == "Invalid CSRF token."

    middleware_client["validate_csrf"].assert_called_once_with(
        middleware_client["user_session"],
        "invalid-csrf-token",
    )


def test_valid_session_and_csrf_allow_action(middleware_client):
    client = middleware_client["client"]
    set_valid_session_cookie(client)

    response = client.post(
        "/middleware-test/action",
        headers={
            "Origin": "http://localhost:5173",
            "X-CSRF-Token": "valid-csrf-token",
        },
    )

    assert response.status_code == 200
    assert response.json["message"] == "Action completed."

    middleware_client["validate_csrf"].assert_called_once_with(
        middleware_client["user_session"],
        "valid-csrf-token",
    )


def test_session_validation_error_returns_500(middleware_client):
    middleware_client["validate_session"].side_effect = RuntimeError(
        "Database unavailable."
    )

    client = middleware_client["client"]
    set_valid_session_cookie(client)

    response = client.get("/middleware-test/protected")

    assert response.status_code == 500
    assert response.json["error"] == (
        "Authentication could not be completed."
    )
