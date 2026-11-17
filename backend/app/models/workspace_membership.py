
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class WorkspaceMembership(db.Model):
    __tablename__ = "workspace_memberships"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "workspace_id",
            name="uq_workspace_memberships_user_workspace",
        ),
        CheckConstraint(
            "role IN ('owner', 'admin', 'developer', 'viewer')",
            name="ck_workspace_memberships_valid_role",
        ),
        Index(
            "ix_workspace_memberships_user_id",
            "user_id",
        ),
        Index(
            "ix_workspace_memberships_workspace_id",
            "workspace_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id"),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

        # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="workspace_memberships",
    )

    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="memberships",
    )

    def __repr__(self) -> str:
        return (
            f"<WorkspaceMembership user_id={self.user_id} "
            f"workspace_id={self.workspace_id} role={self.role}>"
        )