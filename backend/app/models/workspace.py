
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Workspace(db.Model):
    __tablename__ = "workspaces"

    __table_args__ = (
        UniqueConstraint(
            "slug",
            name="uq_workspaces_slug",
        ),
        Index(
            "uq_workspaces_personal_creator",
            "created_by",
            unique=True,
            postgresql_where=text("kind = 'personal'"),
        ),
        CheckConstraint(
            "kind IN ('personal', 'team')",
            name="ck_workspaces_valid_kind",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    kind: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
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
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_workspaces",
        foreign_keys=[created_by],
    )

    memberships: Mapped[list["WorkspaceMembership"]] = relationship(
        "WorkspaceMembership",
        back_populates="workspace",
    )

    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="workspace",
    )

    audit_events: Mapped[list["AuditEvent"]] = relationship(
        "AuditEvent",
        back_populates="workspace",
    )

    def __repr__(self) -> str:
        return f"<Workspace name={self.name} kind={self.kind}>"