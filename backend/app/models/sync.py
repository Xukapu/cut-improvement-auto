from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class SyncDevice(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Устройство пользователя, участвующее в синхронизации."""

    __tablename__ = "sync_devices"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "device_key",
            name="user_device_key",
        ),
        Index(
            "ix_sync_devices_user_id",
            "user_id",
        ),
        Index(
            "ix_sync_devices_last_seen_at",
            "last_seen_at",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "app_users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    device_key: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
    )

    device_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    platform: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class SyncOperation(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Применённая offline-операция.

    operation_id приходит с устройства и обеспечивает идемпотентность.
    """

    __tablename__ = "sync_operations"

    __table_args__ = (
        UniqueConstraint(
            "operation_id",
            name="sync_operation_id",
        ),
        Index(
            "ix_sync_operations_device_id",
            "device_id",
        ),
        Index(
            "ix_sync_operations_user_id",
            "user_id",
        ),
        Index(
            "ix_sync_operations_entity_id",
            "entity_id",
        ),
    )

    operation_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
    )

    device_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sync_devices.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "app_users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    operation_kind: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    entity_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
    )

    result_number: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
