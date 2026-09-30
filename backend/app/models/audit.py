from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import UUIDPrimaryKeyMixin


class AuditLog(
    UUIDPrimaryKeyMixin,
    Base,
):
    """Неизменяемая запись журнала действий."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index(
            "ix_audit_logs_created_at",
            "created_at",
        ),
        Index(
            "ix_audit_logs_actor_user_id",
            "actor_user_id",
        ),
        Index(
            "ix_audit_logs_entity",
            "entity_type",
            "entity_number",
        ),
    )

    event_number: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        nullable=False,
        unique=True,
    )

    actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "app_users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    actor_login: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    actor_role: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    entity_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    entity_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
    )

    entity_number: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    old_values: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    new_values: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
