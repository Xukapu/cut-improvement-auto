from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class WorkParticipationResponse(BaseModel):
    enabled: bool

    employee_number: int | None
    employee_name: str

    rate_percent: Decimal | None


class WorkParticipationUpdate(BaseModel):
    enabled: bool

    rate_percent: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        decimal_places=2,
    )

    @model_validator(mode="after")
    def validate_rate(
        self,
    ) -> "WorkParticipationUpdate":
        if self.enabled and self.rate_percent is None:
            raise ValueError("Укажите ставку исполнителя.")

        return self
