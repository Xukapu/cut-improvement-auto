from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class EmployeeCreate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=200,
    )

    rate_percent: Decimal = Field(
        ge=0,
        le=100,
        decimal_places=2,
    )

    @field_validator("full_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("ФИО не может быть пустым.")

        return value


class EmployeeUpdate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=200,
    )

    is_active: bool

    @field_validator("full_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("ФИО не может быть пустым.")

        return value


class EmployeeRateUpdate(BaseModel):
    rate_percent: Decimal = Field(
        ge=0,
        le=100,
        decimal_places=2,
    )


class EmployeePublicResponse(BaseModel):
    employee_number: int
    full_name: str
    is_active: bool


class EmployeeFinancialResponse(EmployeePublicResponse):
    current_rate_percent: Decimal


class EmployeeRateHistoryItem(BaseModel):
    rate_percent: Decimal
    effective_from: datetime
    effective_to: datetime | None


class EmployeeRateHistoryResponse(BaseModel):
    employee_number: int
    full_name: str
    rates: list[EmployeeRateHistoryItem]
