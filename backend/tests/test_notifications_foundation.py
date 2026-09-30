import app.models  # noqa: F401
from app.db.base import Base
from app.models.notification import (
    NotificationChannel,
    NotificationKind,
    NotificationStatus,
    ServiceReminderStatus,
)
from sqlalchemy import CheckConstraint


def test_notification_tables_registered() -> None:
    assert "client_notification_preferences" in Base.metadata.tables
    assert "customer_notifications" in Base.metadata.tables
    assert "service_reminders" in Base.metadata.tables


def test_notification_enum_values() -> None:
    assert NotificationChannel.SMS.value == "sms"
    assert NotificationChannel.MAX.value == "max"

    assert NotificationKind.APPOINTMENT_CONFIRMATION.value == "appointment_confirmation"
    assert NotificationKind.APPOINTMENT_REMINDER.value == "appointment_reminder"
    assert NotificationKind.SERVICE_REMINDER.value == "service_reminder"

    assert NotificationStatus.PREPARED.value == "prepared"
    assert NotificationStatus.SENT.value == "sent"
    assert NotificationStatus.FAILED.value == "failed"
    assert NotificationStatus.CANCELLED.value == "cancelled"


def test_service_reminder_enum_values() -> None:
    assert ServiceReminderStatus.PLANNED.value == "planned"
    assert ServiceReminderStatus.COMPLETED.value == "completed"
    assert ServiceReminderStatus.CANCELLED.value == "cancelled"


def test_service_reminder_has_due_condition_constraint() -> None:
    table = Base.metadata.tables["service_reminders"]

    names = {
        constraint.name
        for constraint in table.constraints
        if isinstance(
            constraint,
            CheckConstraint,
        )
    }

    assert "ck_service_reminders_due_condition" in names
    assert "ck_service_reminders_due_mileage_non_negative" in names


def test_notification_preference_defaults_are_safe() -> None:
    table = Base.metadata.tables["client_notification_preferences"]

    assert str(table.c.sms_enabled.server_default.arg).lower() == "false"

    assert str(table.c.max_enabled.server_default.arg).lower() == "false"
