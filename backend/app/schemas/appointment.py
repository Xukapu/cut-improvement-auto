from datetime import date, time
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.models.appointment import AppointmentStatus


class AppointmentWrite(BaseModel):
    client_number: int = Field(ge=1)
    vehicle_number: int = Field(ge=1)

    appointment_date: date
    appointment_time: time

    reason: str = Field(
        min_length=2,
        max_length=1000,
    )

    comment: str | None = Field(
        default=None,
        max_length=2000,
    )

    status: AppointmentStatus = AppointmentStatus.SCHEDULED

    @field_validator("reason")
    @classmethod
    def normalize_reason(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Причина обращения не может быть пустой.")

        return value

    @field_validator("comment")
    @classmethod
    def normalize_comment(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class AppointmentCreate(AppointmentWrite):
    pass


class AppointmentUpdate(AppointmentWrite):
    pass


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    appointment_number: int

    client_number: int
    client_name: str

    vehicle_number: int
    license_plate: str

    appointment_date: date
    appointment_time: time

    reason: str
    comment: str | None

    status: AppointmentStatus


class AppointmentListResponse(BaseModel):
    items: list[AppointmentResponse]
    total: int
    limit: int
    offset: int
