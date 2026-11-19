
import hashlib
import secrets
from flask import current_app
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import User, UserSession


SESSION_ABSOLUTE_LIFETIME = timedelta(days=7)
SESSION_IDLE_TIMEOUT = timedelta(hours=24)
SESSION_ACTIVITY_UPDATE_INTERVAL = timedelta(minutes=5)


@dataclass(frozen=True)
class CreatedSession:
    """Contains newly created session credentials."""

    session: UserSession
    session_token: str
    csrf_token: str


def _hash_token(token: str) -> str:
    """Return a SHA-256 hexadecimal digest of a token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(user: User) -> CreatedSession:
    """
    Create a new server-side session for an active user.

    Only token hashes are persisted. Raw tokens are returned
    once for delivery to the client.
    """
    if not isinstance(user, User) or not user.is_active:
        raise ValueError("An active user is required.")

    now = datetime.now(timezone.utc)

    session_token = secrets.token_urlsafe(32)

    from app.services.csrf_service import (
        derive_csrf_token,
        hash_csrf_token,
    )

    csrf_token = derive_csrf_token(
        session_token,
        current_app.config["SECRET_KEY"],
    )

    user_session = UserSession(
        user_id=user.id,
        token_hash=_hash_token(session_token),
        csrf_token_hash=hash_csrf_token(csrf_token),
        expires_at=now + SESSION_ABSOLUTE_LIFETIME,
        created_at=now,
        last_seen_at=now,
    )

    try:
        db.session.add(user_session)
        db.session.commit()

        return CreatedSession(
            session=user_session,
            session_token=session_token,
            csrf_token=csrf_token,
        )

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise RuntimeError(
            "Session creation could not be completed."
        ) from exc


def _as_utc(value: datetime) -> datetime:
    """Normalize database datetimes to timezone-aware UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def validate_session(session_token: str) -> UserSession | None:
    """
    Validate a raw session token.

    Returns the active UserSession when valid.
    Returns None when the token is invalid, expired,
    revoked, idle-expired, or belongs to an inactive user.
    """
    if not isinstance(session_token, str) or not session_token:
        return None

    try:
        token_hash = _hash_token(session_token)

        user_session = db.session.scalar(
            select(UserSession)
            .where(UserSession.token_hash == token_hash)
            .with_for_update()
)

        if user_session is None:
            return None

        if user_session.revoked_at is not None:
            return None

        now = datetime.now(timezone.utc)

        expires_at = _as_utc(user_session.expires_at)
        last_seen_at = _as_utc(user_session.last_seen_at)

        is_expired = now >= expires_at
        is_idle_expired = (
            now - last_seen_at >= SESSION_IDLE_TIMEOUT
        )

        if (
            is_expired
            or is_idle_expired
            or not user_session.user.is_active
        ):
            user_session.revoked_at = now
            db.session.commit()
            return None

        if (
            now - last_seen_at
            >= SESSION_ACTIVITY_UPDATE_INTERVAL
        ):
            user_session.last_seen_at = now
            db.session.commit()

        return user_session

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise RuntimeError(
            "Session validation could not be completed."
        ) from exc



def revoke_session(session_token: str) -> bool:
    """
    Revoke the session associated with a raw session token.

    Returns True if an active session was revoked.
    Returns False if the token is invalid or already revoked.
    """
    if not isinstance(session_token, str) or not session_token:
        return False

    try:
        token_hash = _hash_token(session_token)

        user_session = db.session.scalar(
            select(UserSession)
            .where(UserSession.token_hash == token_hash)
            .with_for_update()
        )

        if user_session is None or user_session.revoked_at is not None:
            return False

        user_session.revoked_at = datetime.now(timezone.utc)
        db.session.commit()

        return True

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise RuntimeError(
            "Session revocation could not be completed."
        ) from exc


def revoke_all_user_sessions(user_id: UUID) -> int:
    """
    Revoke all currently active sessions belonging to a user.

    Returns the number of sessions revoked.
    """
    if not isinstance(user_id, UUID):
        raise ValueError("A valid user ID is required.")

    try:
        active_sessions = db.session.scalars(
            select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.revoked_at.is_(None),
            )
        ).all()

        now = datetime.now(timezone.utc)

        for user_session in active_sessions:
            user_session.revoked_at = now

        db.session.commit()

        return len(active_sessions)

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise RuntimeError(
            "User session revocation could not be completed."
        ) from exc