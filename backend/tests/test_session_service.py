import hashlib

import pytest
from sqlalchemy import select

from app.extensions import db
from app.models import User, UserSession
from app.services.auth_service import register_user
from app.services.session_service import create_session
from datetime import datetime, timedelta, timezone

from app.services.session_service import (
    create_session,
    revoke_all_user_sessions,
    revoke_session,
    validate_session,
)

def _create_test_user():
    return register_user(
        full_name="Ankit Kumar",
        email="ankit@example.com",
        password="CloudForge-Secure-2026",
    )


def test_create_session_for_active_user(app):
    with app.app_context():
        user = _create_test_user()

        result = create_session(user)

        assert result.session is not None
        assert result.session.user_id == user.id
        assert result.session.revoked_at is None
        assert result.session.expires_at > result.session.created_at
        assert result.session_token
        assert result.csrf_token


def test_session_stores_only_token_hashes(app):
    with app.app_context():
        user = _create_test_user()

        result = create_session(user)

        stored_session = db.session.scalar(
            select(UserSession).where(
                UserSession.id == result.session.id
            )
        )

        assert stored_session is not None

        expected_session_hash = hashlib.sha256(
            result.session_token.encode("utf-8")
        ).hexdigest()

        expected_csrf_hash = hashlib.sha256(
            result.csrf_token.encode("utf-8")
        ).hexdigest()

        assert stored_session.token_hash == expected_session_hash
        assert stored_session.csrf_token_hash == expected_csrf_hash

        assert stored_session.token_hash != result.session_token
        assert stored_session.csrf_token_hash != result.csrf_token


def test_create_session_rejects_inactive_user(app):
    with app.app_context():
        user = _create_test_user()

        user.is_active = False
        db.session.commit()

        with pytest.raises(ValueError):
            create_session(user)

        sessions = db.session.scalars(
            select(UserSession).where(
                UserSession.user_id == user.id
            )
        ).all()

        assert sessions == []


def test_user_can_have_multiple_independent_sessions(app):
    with app.app_context():
        user = _create_test_user()

        first_session = create_session(user)
        second_session = create_session(user)

        assert first_session.session.id != second_session.session.id
        assert first_session.session_token != second_session.session_token
        assert first_session.csrf_token != second_session.csrf_token

        sessions = db.session.scalars(
            select(UserSession).where(
                UserSession.user_id == user.id
            )
        ).all()

        assert len(sessions) == 2



def test_validate_session_accepts_valid_session(app):
    with app.app_context():
        user = _create_test_user()
        created = create_session(user)

        validated = validate_session(created.session_token)

        assert validated is not None
        assert validated.id == created.session.id
        assert validated.user_id == user.id


def test_validate_session_rejects_unknown_token(app):
    with app.app_context():
        validated = validate_session("unknown-session-token")

        assert validated is None


def test_validate_session_rejects_absolute_expiry(app):
    with app.app_context():
        user = _create_test_user()
        created = create_session(user)

        created.session.expires_at = (
            datetime.now(timezone.utc) - timedelta(seconds=1)
        )
        db.session.commit()

        validated = validate_session(created.session_token)

        assert validated is None
        assert created.session.revoked_at is not None


def test_validate_session_rejects_idle_expiry(app):
    with app.app_context():
        user = _create_test_user()
        created = create_session(user)

        created.session.last_seen_at = (
            datetime.now(timezone.utc) - timedelta(hours=25)
        )
        db.session.commit()

        validated = validate_session(created.session_token)

        assert validated is None
        assert created.session.revoked_at is not None


def test_validate_session_rejects_revoked_session(app):
    with app.app_context():
        user = _create_test_user()
        created = create_session(user)

        created.session.revoked_at = datetime.now(timezone.utc)
        db.session.commit()

        validated = validate_session(created.session_token)

        assert validated is None


def test_validate_session_rejects_inactive_user(app):
    with app.app_context():
        user = _create_test_user()
        created = create_session(user)

        user.is_active = False
        db.session.commit()

        validated = validate_session(created.session_token)

        assert validated is None
        assert created.session.revoked_at is not None



def test_revoke_session_invalidates_only_current_session(app):
    with app.app_context():
        user = _create_test_user()

        first = create_session(user)
        second = create_session(user)

        assert revoke_session(first.session_token) is True

        assert validate_session(first.session_token) is None
        assert validate_session(second.session_token) is not None


def test_revoke_session_rejects_unknown_token(app):
    with app.app_context():
        assert revoke_session("unknown-session-token") is False


def test_revoke_session_is_idempotent(app):
    with app.app_context():
        user = _create_test_user()
        created = create_session(user)

        assert revoke_session(created.session_token) is True
        assert revoke_session(created.session_token) is False


def test_revoke_all_user_sessions(app):
    with app.app_context():
        user = _create_test_user()

        first = create_session(user)
        second = create_session(user)

        revoked_count = revoke_all_user_sessions(user.id)

        assert revoked_count == 2
        assert validate_session(first.session_token) is None
        assert validate_session(second.session_token) is None


def test_revoke_all_sessions_does_not_affect_another_user(app):
    with app.app_context():
        first_user = _create_test_user()

        second_user = register_user(
            full_name="Another User",
            email="another@example.com",
            password="Another-Secure-Password-2026",
        )

        first_session = create_session(first_user)
        second_session = create_session(second_user)

        revoked_count = revoke_all_user_sessions(first_user.id)

        assert revoked_count == 1
        assert validate_session(first_session.session_token) is None
        assert validate_session(second_session.session_token) is not None
