from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.notification import (
    NotificationChannel,
    NotificationKind,
    NotificationStatus,
    ServiceReminderStatus,
)


class NotificationPreferenceUpdate(BaseModel):
    sms_enabled: bool
    max_enabled: bool
    appointment_confirmation_enabled: bool
    appointment_reminder_enabled: bool
    service_reminder_enabled: bool


class NotificationPreferenceResponse(BaseModel):
    client_id: UUID
    client_number: int
    client_name: str
    phone_primary: str

    sms_enabled: bool
    max_enabled: bool
    max_connected: bool

    appointment_confirmation_enabled: bool
    appointment_reminder_enabled: bool
    service_reminder_enabled: bool


class CustomerNotificationResponse(BaseModel):
    id: UUID

    client_number: int | None
    client_name: str | None
    vehicle_number: int | None
    appointment_number: int | None

    channel: NotificationChannel
    kind: NotificationKind
    status: NotificationStatus

    message_text: str
    scheduled_for: datetime
    sent_at: datetime | None
    error_message: str | None
    created_at: datetime


class ServiceReminderCreate(BaseModel):
    client_number: int = Field(ge=1)
    vehicle_number: int = Field(ge=1)

    work_name: str = Field(
        min_length=1,
        max_length=500,
    )

    due_date: date | None = None

    due_mileage: int | None = Field(
        default=None,
        ge=0,
    )

    message_text: str = Field(
        min_length=1,
        max_length=2000,
    )


class ServiceReminderResponse(BaseModel):
    id: UUID

    client_number: int
    client_name: str

    vehicle_number: int
    vehicle_name: str

    work_name: str

    due_date: date | None
    due_mileage: int | None

    message_text: str
    status: ServiceReminderStatus

    completed_at: datetime | None

    created_at: datetime
    updated_at: datetime


class PrepareDueNotificationsResponse(BaseModel):
    prepared_count: int
