from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    false,
    true,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class NotificationChannel(StrEnum):
    SMS = "sms"
    MAX = "max"


class NotificationKind(StrEnum):
    APPOINTMENT_CONFIRMATION = "appointment_confirmation"
    APPOINTMENT_REMINDER = "appointment_reminder"
    SERVICE_REMINDER = "service_reminder"


class NotificationStatus(StrEnum):
    PREPARED = "prepared"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ServiceReminderStatus(StrEnum):
    PLANNED = "planned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ClientNotificationPreference(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "client_notification_preferences"

    client_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "clients.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    sms_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )

    max_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )

    appointment_confirmation_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    appointment_reminder_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    service_reminder_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    max_user_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )


class CustomerNotification(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "customer_notifications"

    client_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "clients.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    vehicle_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "vehicles.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    appointment_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "appointments.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    channel: Mapped[NotificationChannel] = mapped_column(
        SQLEnum(
            NotificationChannel,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            name="notification_channel",
            native_enum=False,
            length=32,
        ),
        nullable=False,
    )

    kind: Mapped[NotificationKind] = mapped_column(
        SQLEnum(
            NotificationKind,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            name="notification_kind",
            native_enum=False,
            length=64,
        ),
        nullable=False,
    )

    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(
            NotificationStatus,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            name="notification_status",
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=NotificationStatus.PREPARED,
        server_default=NotificationStatus.PREPARED.value,
    )

    message_text: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    provider_message_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "channel IN ('sms', 'max')",
            name="channel_valid",
        ),
        CheckConstraint(
            "kind IN ('appointment_confirmation', 'appointment_reminder', 'service_reminder')",
            name="kind_valid",
        ),
        CheckConstraint(
            "status IN ('prepared', 'sent', 'failed', 'cancelled')",
            name="status_valid",
        ),
        Index(
            "ix_customer_notifications_status_scheduled",
            "status",
            "scheduled_for",
        ),
    )


class ServiceReminder(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "service_reminders"

    client_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "clients.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    vehicle_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "vehicles.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    work_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        index=True,
    )

    due_mileage: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    message_text: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    status: Mapped[ServiceReminderStatus] = mapped_column(
        SQLEnum(
            ServiceReminderStatus,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            name="service_reminder_status",
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=ServiceReminderStatus.PLANNED,
        server_default=ServiceReminderStatus.PLANNED.value,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "due_date IS NOT NULL OR due_mileage IS NOT NULL",
            name="due_condition",
        ),
        CheckConstraint(
            "due_mileage IS NULL OR due_mileage >= 0",
            name="due_mileage_non_negative",
        ),
        CheckConstraint(
            "status IN ('planned', 'completed', 'cancelled')",
            name="status_valid",
        ),
    )
