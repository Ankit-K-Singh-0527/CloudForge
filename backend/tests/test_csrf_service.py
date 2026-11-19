
from app.services.csrf_service import (
    hash_csrf_token,
    validate_csrf_token,
    derive_csrf_token,
)
from app.services.session_service import create_session


def test_hash_csrf_token_returns_sha256_hash():
    token = "test-csrf-token"

    result = hash_csrf_token(token)

    assert result != token
    assert len(result) == 64


def test_validate_csrf_token_accepts_correct_token(app):
    with app.app_context():
        from app.extensions import db
        from app.models import User

        user = User(
            email="csrf@example.com",
            full_name="CSRF Test User",
        )
        db.session.add(user)
        db.session.commit()

        created = create_session(user)

        assert validate_csrf_token(
            created.session,
            created.csrf_token,
        ) is True


def test_validate_csrf_token_rejects_incorrect_token(app):
    with app.app_context():
        from app.extensions import db
        from app.models import User

        user = User(
            email="csrf-invalid@example.com",
            full_name="CSRF Test User",
        )
        db.session.add(user)
        db.session.commit()

        created = create_session(user)

        assert validate_csrf_token(
            created.session,
            "incorrect-token",
        ) is False


def test_validate_csrf_token_rejects_empty_token(app):
    with app.app_context():
        from app.extensions import db
        from app.models import User

        user = User(
            email="csrf-empty@example.com",
            full_name="CSRF Test User",
        )
        db.session.add(user)
        db.session.commit()

        created = create_session(user)

        assert validate_csrf_token(
            created.session,
            "",
        ) is False


def test_derive_csrf_token_is_deterministic():
    first = derive_csrf_token("session-123", "test-secret")
    second = derive_csrf_token("session-123", "test-secret")

    assert first == second


def test_derive_csrf_token_changes_with_secret():
    first = derive_csrf_token("session-123", "secret-one")
    second = derive_csrf_token("session-123", "secret-two")

    assert first != second


def test_derive_csrf_token_changes_with_session():
    first = derive_csrf_token("session-one", "test-secret")
    second = derive_csrf_token("session-two", "test-secret")

    assert first != second


def test_derive_csrf_token_rejects_empty_session_token():
    import pytest

    with pytest.raises(ValueError):
        derive_csrf_token("", "test-secret")


def test_derive_csrf_token_rejects_empty_secret():
    import pytest

    with pytest.raises(ValueError):
        derive_csrf_token("session-123", "")