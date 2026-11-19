
import hashlib
import hmac

from app.models import UserSession


def derive_csrf_token(session_token: str, secret_key: str) -> str:
    """
    Deterministically derive a CSRF token from a session token.

    Domain separation ensures this derived value is used specifically
    for CSRF protection.
    """
    if not isinstance(session_token, str) or not session_token:
        raise ValueError("A valid session token is required.")

    if not isinstance(secret_key, str) or not secret_key:
        raise ValueError("A valid secret key is required.")

    message = f"cloudforge:csrf:v1:{session_token}".encode("utf-8")

    return hmac.new(
        secret_key.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()


def hash_csrf_token(token: str) -> str:
    """Return a SHA-256 hexadecimal digest of a CSRF token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def validate_csrf_token(
    user_session: UserSession,
    csrf_token: str,
) -> bool:
    """
    Validate a CSRF token against the authenticated session.

    The comparison is performed in constant time.
    """
    if not isinstance(user_session, UserSession):
        return False

    if not isinstance(csrf_token, str) or not csrf_token:
        return False

    supplied_hash = hash_csrf_token(csrf_token)

    return hmac.compare_digest(
        user_session.csrf_token_hash,
        supplied_hash,
    )
