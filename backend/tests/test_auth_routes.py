
REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/auth/me"
CSRF_URL = "/api/v1/auth/csrf"

TRUSTED_ORIGIN = "http://localhost:5173"

REGISTRATION_DATA = {
    "full_name": "CloudForge Test User",
    "email": "cloudforge.routes@example.com",
    "password": "CloudForge-Secure-Password-2026",
}


def register_user(client):
    return client.post(
        REGISTER_URL,
        json=REGISTRATION_DATA,
        headers={"Origin": TRUSTED_ORIGIN},
    )


def test_registration_creates_session_and_sets_cookie(client):
    response = register_user(client)

    assert response.status_code == 201

    data = response.get_json()

    assert data["user"]["email"] == REGISTRATION_DATA["email"]
    assert data["user"]["full_name"] == REGISTRATION_DATA["full_name"]
    assert data["csrf_token"]

    cookie_header = response.headers["Set-Cookie"]

    assert "cloudforge_session=" in cookie_header
    assert "HttpOnly" in cookie_header
    assert "SameSite=Lax" in cookie_header


def test_registration_rejects_untrusted_origin(client):
    response = client.post(
        REGISTER_URL,
        json=REGISTRATION_DATA,
        headers={"Origin": "https://untrusted.example"},
    )

    assert response.status_code == 403


def test_registration_rejects_invalid_json(client):
    response = client.post(
        REGISTER_URL,
        data="invalid-json",
        content_type="application/json",
        headers={"Origin": TRUSTED_ORIGIN},
    )

    assert response.status_code == 400


def test_current_user_returns_authenticated_profile(client):
    register_user(client)

    response = client.get(ME_URL)

    assert response.status_code == 200

    data = response.get_json()

    assert data["user"]["email"] == REGISTRATION_DATA["email"]
    assert data["user"]["full_name"] == REGISTRATION_DATA["full_name"]


def test_current_user_rejects_missing_session(client):
    response = client.get(ME_URL)

    assert response.status_code == 401


def test_csrf_endpoint_returns_session_token(client):
    register_response = register_user(client)

    original_token = register_response.get_json()["csrf_token"]

    response = client.get(CSRF_URL)

    assert response.status_code == 200
    assert response.get_json()["csrf_token"] == original_token


def test_login_creates_session_for_valid_credentials(client):
    register_user(client)

    client.delete_cookie("cloudforge_session")

    response = client.post(
        LOGIN_URL,
        json={
            "email": REGISTRATION_DATA["email"],
            "password": REGISTRATION_DATA["password"],
        },
        headers={"Origin": TRUSTED_ORIGIN},
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["user"]["email"] == REGISTRATION_DATA["email"]
    assert data["csrf_token"]
    assert "cloudforge_session=" in response.headers["Set-Cookie"]


def test_login_rejects_incorrect_credentials(client):
    register_user(client)

    client.delete_cookie("cloudforge_session")

    response = client.post(
        LOGIN_URL,
        json={
            "email": REGISTRATION_DATA["email"],
            "password": "Incorrect-Password-2026",
        },
        headers={"Origin": TRUSTED_ORIGIN},
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid email or password."


def test_logout_requires_csrf_token(client):
    register_user(client)

    response = client.post(
        LOGOUT_URL,
        headers={"Origin": TRUSTED_ORIGIN},
    )

    assert response.status_code == 403

    # The session must remain valid after a rejected logout.
    profile_response = client.get(ME_URL)
    assert profile_response.status_code == 200


def test_logout_revokes_session_and_clears_cookie(client):
    register_response = register_user(client)

    csrf_token = register_response.get_json()["csrf_token"]

    response = client.post(
        LOGOUT_URL,
        headers={
            "Origin": TRUSTED_ORIGIN,
            "X-CSRF-Token": csrf_token,
        },
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Logout successful."

    cookie_header = response.headers["Set-Cookie"]

    assert "cloudforge_session=" in cookie_header
    assert "Max-Age=0" in cookie_header

    profile_response = client.get(ME_URL)

    assert profile_response.status_code == 401


def test_logout_rejects_untrusted_origin(client):
    register_response = register_user(client)

    csrf_token = register_response.get_json()["csrf_token"]

    response = client.post(
        LOGOUT_URL,
        headers={
            "Origin": "https://untrusted.example",
            "X-CSRF-Token": csrf_token,
        },
    )

    assert response.status_code == 403
