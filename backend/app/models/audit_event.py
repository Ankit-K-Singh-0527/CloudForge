
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class AuditEvent(db.Model):
    __tablename__ = "audit_events"

    __table_args__ = (
        Index(
            "ix_audit_events_workspace_created",
            "workspace_id",
            "created_at",
        ),
        Index(
            "ix_audit_events_actor_created",
            "actor_user_id",
            "created_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    workspace_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workspaces.id", ondelete="SET NULL"),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    resource_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
    )

    metadata_: Mapped[dict] = mapped_column(
    "metadata",
    JSON().with_variant(JSONB(), "postgresql"),
    nullable=False,
    server_default=text("'{}'"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    actor: Mapped["User | None"] = relationship(
        "User",
        back_populates="audit_events",
        foreign_keys=[actor_user_id],
    )

    workspace: Mapped["Workspace | None"] = relationship(
        "Workspace",
        back_populates="audit_events",
    )

    def __repr__(self) -> str:
        return (
            f"<AuditEvent action={self.action} "
            f"resource_type={self.resource_type}>"
        )