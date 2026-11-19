
from flask import Blueprint, current_app, g, jsonify, request

from app.middleware import (
    require_auth,
    require_csrf,
    validate_request_origin,
)
from app.services.auth_service import (
    InvalidRegistrationData,
    LoginError,
    LoginServiceError,
    LogoutServiceError,
    RegistrationConflict,
    RegistrationServiceError,
    register_user,
    authenticate_user,
    logout_user,
)
from app.services.csrf_service import (
    derive_csrf_token,
    validate_csrf_token,
)
from app.services.session_service import (
    create_session,
    validate_session,
)


auth_bp = Blueprint("auth", __name__)


def _user_response(user):
    """Return only safe, public user information."""
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "email_verified_at": (
            user.email_verified_at.isoformat()
            if user.email_verified_at
            else None
        ),
        "created_at": (
            user.created_at.isoformat()
            if user.created_at
            else None
        ),
    }


def _set_session_cookie(response, session_token):
    """Attach the opaque session token as a secure browser cookie."""
    response.set_cookie(
        current_app.config["AUTH_COOKIE_NAME"],
        session_token,
        max_age=604800,
        httponly=current_app.config["AUTH_COOKIE_HTTPONLY"],
        secure=current_app.config["AUTH_COOKIE_SECURE"],
        samesite=current_app.config["AUTH_COOKIE_SAMESITE"],
        path=current_app.config["AUTH_COOKIE_PATH"],
    )

    return response


def _clear_session_cookie(response):
    """Remove the browser's session cookie."""
    response.delete_cookie(
        current_app.config["AUTH_COOKIE_NAME"],
        httponly=current_app.config["AUTH_COOKIE_HTTPONLY"],
        secure=current_app.config["AUTH_COOKIE_SECURE"],
        samesite=current_app.config["AUTH_COOKIE_SAMESITE"],
        path=current_app.config["AUTH_COOKIE_PATH"],
    )

    return response


def _create_auth_response(user, status_code=200):
    """Create a session and return safe authentication data."""
    created_session = create_session(user)

    response = jsonify({
        "message": "Authentication successful.",
        "user": _user_response(user),
        "csrf_token": created_session.csrf_token,
    })

    response.status_code = status_code

    return _set_session_cookie(
        response,
        created_session.session_token,
    )


@auth_bp.post("/auth/register")
def register():
    """Register a user and create their initial browser session."""
    origin_error = validate_request_origin()

    if origin_error is not None:
        return origin_error

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON request body is required."
        }), 400

    try:
        user = register_user(
            full_name=data.get("full_name"),
            email=data.get("email"),
            password=data.get("password"),
        )

        return _create_auth_response(user, 201)

    except InvalidRegistrationData as exc:
        return jsonify({"error": str(exc)}), 400

    except RegistrationConflict:
        return jsonify({
            "error": "Registration could not be completed."
        }), 409

    except RegistrationServiceError:
        current_app.logger.exception(
            "User registration failed."
        )
        return jsonify({
            "error": "Registration could not be completed."
        }), 500

    except (RuntimeError, ValueError):
        current_app.logger.exception(
            "Registration session creation failed."
        )
        return jsonify({
            "error": "Registration could not be completed."
        }), 500


@auth_bp.post("/auth/login")
def login():
    """Authenticate a user and create a browser session."""
    origin_error = validate_request_origin()

    if origin_error is not None:
        return origin_error

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON request body is required."
        }), 400

    try:
        user = authenticate_user(
            email=data.get("email"),
            password=data.get("password"),
        )

        return _create_auth_response(user)

    except LoginError:
        return jsonify({
            "error": "Invalid email or password."
        }), 401

    except LoginServiceError:
        current_app.logger.exception(
            "User authentication failed."
        )
        return jsonify({
            "error": "Login could not be completed."
        }), 500

    except (RuntimeError, ValueError):
        current_app.logger.exception(
            "Login session creation failed."
        )
        return jsonify({
            "error": "Login could not be completed."
        }), 500



@auth_bp.post("/auth/logout")
@require_auth
@require_csrf
def logout():
    """Revoke the current session and clear its browser cookie."""
    try:
        revoked = logout_user(g.session_token)

        if not revoked:
            response = jsonify({
                "message": "Session is already invalidated."
            })
            return _clear_session_cookie(response), 200

        response = jsonify({
            "message": "Logout successful."
        })

        return _clear_session_cookie(response), 200

    except LogoutServiceError:
        current_app.logger.exception(
            "User logout failed."
        )
        return jsonify({
            "error": "Logout could not be completed."
        }), 500


@auth_bp.get("/auth/me")
@require_auth
def get_current_user():
    """Return the authenticated user's public profile."""
    return jsonify({
        "user": _user_response(g.current_user)
    }), 200


@auth_bp.get("/auth/csrf")
@require_auth
def get_csrf_token():
    """Return the deterministic CSRF token for the current session."""
    try:
        csrf_token = derive_csrf_token(
            g.session_token,
            current_app.config["SECRET_KEY"],
        )

        if not validate_csrf_token(
            g.user_session,
            csrf_token,
        ):
            current_app.logger.error(
                "Stored CSRF token hash did not match its derived token."
            )
            return jsonify({
                "error": "CSRF token could not be validated."
            }), 500

        return jsonify({
            "csrf_token": csrf_token
        }), 200

    except (RuntimeError, ValueError):
        current_app.logger.exception(
            "CSRF token retrieval failed."
        )
        return jsonify({
            "error": "CSRF token could not be retrieved."
        }), 500
