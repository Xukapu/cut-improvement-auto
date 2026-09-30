from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.work_order import WorkOrderStatus


class WorkOrderCreate(BaseModel):
    client_number: int = Field(ge=1)
    vehicle_number: int = Field(ge=1)

    appointment_number: int | None = Field(
        default=None,
        ge=1,
    )

    reason: str = Field(
        min_length=2,
        max_length=2000,
    )

    mileage: int | None = Field(
        default=None,
        ge=0,
    )

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Причина обращения не может быть пустой.")

        return value


class WorkOrderUpdate(BaseModel):
    reason: str = Field(
        min_length=2,
        max_length=2000,
    )

    mileage: int | None = Field(
        default=None,
        ge=0,
    )

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Причина обращения не может быть пустой.")

        return value


class WorkOrderStatusUpdate(BaseModel):
    status: WorkOrderStatus


class WorkOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    work_order_number: int

    client_number: int
    client_name: str

    vehicle_number: int
    license_plate: str

    appointment_number: int | None

    status: WorkOrderStatus

    reason: str
    mileage: int | None

    created_at: datetime
    started_at: datetime | None
    ready_at: datetime | None
    issued_at: datetime | None


class WorkOrderListResponse(BaseModel):
    items: list[WorkOrderResponse]
    total: int
    limit: int
    offset: int
