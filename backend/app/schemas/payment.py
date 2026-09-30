from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.payment import PaymentMethod


class PaymentWrite(BaseModel):
    amount: Decimal = Field(
        gt=0,
        decimal_places=2,
    )

    method: PaymentMethod

    comment: str | None = Field(
        default=None,
        max_length=1000,
    )

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


class PaymentCreate(PaymentWrite):
    pass


class PaymentUpdate(PaymentWrite):
    pass


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_number: int
    amount: Decimal
    method: PaymentMethod
    comment: str | None
    paid_at: datetime


class PaymentSummaryResponse(BaseModel):
    work_order_number: int

    works_total: Decimal
    parts_total: Decimal
    repair_total: Decimal

    paid_amount: Decimal
    debt_amount: Decimal

    payments: list[PaymentResponse]
