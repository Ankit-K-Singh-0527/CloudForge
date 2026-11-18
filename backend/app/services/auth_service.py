import re
import secrets
import unicodedata

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models import (
    AuditEvent,
    User,
    UserCredential,
    Workspace,
    WorkspaceMembership,
)
from app.services.password_service import (
    hash_password,
    verify_password
)

class RegistrationError(Exception):
    """Base exception for registration failures."""


class InvalidRegistrationData(RegistrationError):
    """Raised when registration input is invalid."""


class RegistrationConflict(RegistrationError):
    """Raised when registration conflicts with existing data."""


class RegistrationServiceError(RegistrationError):
    """Raised when registration cannot be completed."""


class LoginError(Exception):
    """Raised when login credentials are invalid."""


class LoginServiceError(Exception):
    """Raised when the login operation cannot be completed."""


def _normalize_name(full_name: str) -> str:
    return " ".join(full_name.split())


def _validate_registration_data(
    full_name: str,
    email: str,
    password: str,
) -> tuple[str, str]:
    if not all(isinstance(value, str) for value in (
        full_name,
        email,
        password,
    )):
        raise InvalidRegistrationData(
            "Invalid registration details."
        )

    normalized_name = _normalize_name(full_name)
    normalized_email = email.strip().lower()

    if not normalized_name or len(normalized_name) > 120:
        raise InvalidRegistrationData(
            "Full name must contain between 1 and 120 characters."
        )

    if not normalized_email or len(normalized_email) > 320:
        raise InvalidRegistrationData(
            "A valid email address is required."
        )

    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.fullmatch(email_pattern, normalized_email):
        raise InvalidRegistrationData(
            "A valid email address is required."
        )

    if not 12 <= len(password) <= 128:
        raise InvalidRegistrationData(
            "Password must contain between 12 and 128 characters."
        )

    return normalized_name, normalized_email


def _generate_workspace_slug(full_name: str) -> str:
    normalized = unicodedata.normalize("NFKD", full_name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    base_slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")

    if not base_slug:
        base_slug = "workspace"

    suffix = secrets.token_hex(4)

    return f"{base_slug}-{suffix}"


def register_user(
    full_name: str,
    email: str,
    password: str,
) -> User:
    """
    Create a user, credential, personal workspace,
    owner membership, and audit event atomically.
    """
    normalized_name, normalized_email = _validate_registration_data(
        full_name,
        email,
        password,
    )

    try:
        existing_user = db.session.scalar(
            select(User).where(User.email == normalized_email)
        )

        if existing_user is not None:
            raise RegistrationConflict(
                "Registration could not be completed."
            )

        try:
            password_hash = hash_password(password)
        except RuntimeError as exc:
            raise RegistrationServiceError(
                "Registration could not be completed."
            ) from exc

        user = User(
            email=normalized_email,
            full_name=normalized_name,
        )

        db.session.add(user)
        db.session.flush()

        credential = UserCredential(
            user_id=user.id,
            password_hash=password_hash,
        )

        workspace = Workspace(
            name=f"{normalized_name}'s Workspace",
            slug=_generate_workspace_slug(normalized_name),
            kind="personal",
            created_by=user.id,
        )

        db.session.add_all([credential, workspace])
        db.session.flush()

        membership = WorkspaceMembership(
            user_id=user.id,
            workspace_id=workspace.id,
            role="owner",
        )

        audit_event = AuditEvent(
            actor_user_id=user.id,
            workspace_id=workspace.id,
            action="user.registered",
            resource_type="user",
            resource_id=user.id,
            metadata_={
                "registration_method": "email_password",
            },
        )

        db.session.add_all([membership, audit_event])
        db.session.commit()

        return user

    except RegistrationError:
        db.session.rollback()
        raise

    except IntegrityError as exc:
        db.session.rollback()
        raise RegistrationConflict(
            "Registration could not be completed."
        ) from exc

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise RegistrationServiceError(
            "Registration could not be completed."
        ) from exc


def authenticate_user(email: str, password: str) -> User:
    """
    Authenticate a user using email and password credentials.

    Returns the authenticated User on success.
    Raises LoginError for invalid credentials.
    Raises LoginServiceError for database failures.
    """
    if not isinstance(email, str) or not isinstance(password, str):
        raise LoginError("Invalid email or password.")

    normalized_email = email.strip().lower()

    if not normalized_email:
        raise LoginError("Invalid email or password.")

    try:
        result = db.session.execute(
            select(User, UserCredential)
            .join(
                UserCredential,
                UserCredential.user_id == User.id,
            )
            .where(User.email == normalized_email)
        ).first()

        if result is None:
            raise LoginError("Invalid email or password.")

        user, credential = result

        if not user.is_active:
            raise LoginError("Invalid email or password.")

        if not verify_password(
            credential.password_hash,
            password,
        ):
            raise LoginError("Invalid email or password.")

        return user

    except LoginError:
        raise

    except SQLAlchemyError as exc:
        db.session.rollback()
        raise LoginServiceError(
            "Login could not be completed."
        ) from exc