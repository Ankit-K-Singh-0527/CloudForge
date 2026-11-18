
import pytest

from sqlalchemy import select

from app.extensions import db
from app.models import (
    AuditEvent,
    User,
    UserCredential,
    Workspace,
    WorkspaceMembership,
)
from app.services.auth_service import (
    InvalidRegistrationData,
    RegistrationConflict,
    register_user,
)
from app.services.password_service import verify_password


def test_registration_creates_all_required_records(app):
    with app.app_context():
        user = register_user(
            full_name="Ankit Kumar",
            email="ANKIT@example.com",
            password="CloudForge-Secure-2026",
        )

        credential = db.session.scalar(
            select(UserCredential).where(
                UserCredential.user_id == user.id
            )
        )

        workspace = db.session.scalar(
            select(Workspace).where(
                Workspace.created_by == user.id
            )
        )

        membership = db.session.scalar(
            select(WorkspaceMembership).where(
                WorkspaceMembership.user_id == user.id
            )
        )

        audit_event = db.session.scalar(
            select(AuditEvent).where(
                AuditEvent.actor_user_id == user.id
            )
        )

        # Verify user details
        assert user.email == "ankit@example.com"
        assert user.full_name == "Ankit Kumar"

        # Verify password credentials
        assert credential is not None
        assert verify_password(
            credential.password_hash,
            "CloudForge-Secure-2026",
        )

        # Verify personal workspace
        assert workspace is not None
        assert workspace.kind == "personal"
        assert workspace.created_by == user.id

        # Verify owner membership
        assert membership is not None
        assert membership.role == "owner"
        assert membership.user_id == user.id
        assert membership.workspace_id == workspace.id

        # Verify audit event
        assert audit_event is not None
        assert audit_event.action == "user.registered"
        assert audit_event.workspace_id == workspace.id


def test_registration_rejects_duplicate_email(app):
    with app.app_context():
        register_user(
            "Ankit Kumar",
            "ankit@example.com",
            "CloudForge-Secure-2026",
        )

        with pytest.raises(RegistrationConflict):
            register_user(
                "Another User",
                "ANKIT@example.com",
                "Another-Secure-Password",
            )

        # Verify the original user still exists
        assert db.session.scalar(
            select(User).where(
                User.email == "ankit@example.com"
            )
        ) is not None

        # Verify no second user was created
        assert db.session.scalar(
            select(User).where(
                User.email == "another@example.com"
            )
        ) is None

        # Verify no workspace was created for the failed registration
        assert db.session.scalar(
            select(Workspace).where(
                Workspace.name == "Another User's Workspace"
            )
        ) is None


@pytest.mark.parametrize(
    ("full_name", "email", "password"),
    [
        ("", "valid@example.com", "CloudForge-Secure-2026"),
        ("A" * 121, "valid@example.com", "CloudForge-Secure-2026"),
        ("Ankit", "invalid-email", "CloudForge-Secure-2026"),
        ("Ankit", "valid@example.com", "short"),
        ("Ankit", "valid@example.com", "A" * 129),
    ],
)
def test_registration_rejects_invalid_data(
    app,
    full_name,
    email,
    password,
):
    with app.app_context():
        with pytest.raises(InvalidRegistrationData):
            register_user(full_name, email, password)


def test_registration_normalizes_full_name(app):
    with app.app_context():
        user = register_user(
            "  Ankit    Kumar  ",
            "ankit@example.com",
            "CloudForge-Secure-2026",
        )

        assert user.full_name == "Ankit Kumar"


def test_registration_does_not_store_plaintext_password(app):
    with app.app_context():
        user = register_user(
            "Ankit Kumar",
            "ankit@example.com",
            "CloudForge-Secure-2026",
        )

        credential = db.session.scalar(
            select(UserCredential).where(
                UserCredential.user_id == user.id
            )
        )

        assert credential is not None
        assert credential.password_hash != "CloudForge-Secure-2026"
        assert credential.password_hash.startswith("$argon2id$")

        assert verify_password(
            credential.password_hash,
            "CloudForge-Secure-2026",
        )

        assert not verify_password(
            credential.password_hash,
            "Wrong-Password-2026",
        )