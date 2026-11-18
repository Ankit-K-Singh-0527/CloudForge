
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    created_workspaces: Mapped[list["Workspace"]] = relationship(
        "Workspace",
        back_populates="creator",
    )

    workspace_memberships: Mapped[list["WorkspaceMembership"]] = relationship(
        "WorkspaceMembership",
        back_populates="user",
    )

        # Authentication relationships
    credential: Mapped["UserCredential | None"] = relationship(
        "UserCredential",
        back_populates="user",
        uselist=False,
    )

    identities: Mapped[list["UserIdentity"]] = relationship(
        "UserIdentity",
        back_populates="user",
    )

    sessions: Mapped[list["UserSession"]] = relationship(
    "UserSession",
    back_populates="user",
    )

    # Project and audit relationships
    created_projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="creator",
        foreign_keys="Project.created_by",
    )

    audit_events: Mapped[list["AuditEvent"]] = relationship(
        "AuditEvent",
        back_populates="actor",
        foreign_keys="AuditEvent.actor_user_id",
    )

    @validates("email")
    def normalize_email(self, key: str, value: str) -> str:
        return value.strip().lower()

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


Index(
    "uq_users_email_lower",
    func.lower(User.email),
    unique=True,
)