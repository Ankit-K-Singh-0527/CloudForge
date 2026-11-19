
from functools import wraps

from flask import current_app, g, jsonify, request

from app.services.csrf_service import validate_csrf_token
from app.services.session_service import validate_session


SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def validate_request_origin():
    """
    Allow requests only from explicitly configured frontend origins.

    Requests without an Origin header are rejected for browser-facing
    authentication endpoints.
    """
    origin = request.headers.get("Origin")

    allowed_origins = current_app.config.get("FRONTEND_ORIGINS", [])

    if not origin or origin not in allowed_origins:
        return jsonify({
            "error": "Untrusted request origin."
        }), 403

    return None


def require_auth(view):
    """
    Require a valid browser session.

    Stores the authenticated session and user in Flask's request context:
        g.user_session
        g.current_user
    """
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        cookie_name = current_app.config["AUTH_COOKIE_NAME"]
        session_token = request.cookies.get(cookie_name)

        if not session_token:
            return jsonify({
                "error": "Authentication required."
            }), 401

        try:
            user_session = validate_session(session_token)
        except RuntimeError:
            current_app.logger.exception(
                "Session validation failed."
            )
            return jsonify({
                "error": "Authentication could not be completed."
            }), 500

        if user_session is None:
            return jsonify({
                "error": "Authentication required."
            }), 401

        g.user_session = user_session
        g.current_user = user_session.user
        g.session_token = session_token

        return view(*args, **kwargs)

    return wrapped_view


def require_csrf(view):
    """
    Require a valid CSRF token for unsafe authenticated requests.
    """
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if request.method in SAFE_METHODS:
            return view(*args, **kwargs)

        origin_error = validate_request_origin()

        if origin_error is not None:
            return origin_error

        csrf_token = request.headers.get("X-CSRF-Token")

        if not csrf_token:
            return jsonify({
                "error": "CSRF token is required."
            }), 403

        user_session = getattr(g, "user_session", None)

        if user_session is None:
            return jsonify({
                "error": "Authentication required."
            }), 401

        if not validate_csrf_token(user_session, csrf_token):
            return jsonify({
                "error": "Invalid CSRF token."
            }), 403

        return view(*args, **kwargs)

    return wrapped_view
