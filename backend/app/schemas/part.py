from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.part import PartProvidedBy

_MONEY = Decimal("0.01")


class PartWrite(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=500,
    )

    quantity: int = Field(
        default=1,
        ge=1,
    )

    unit_price: Decimal = Field(
        ge=0,
        decimal_places=2,
    )

    supplier: str | None = Field(
        default=None,
        max_length=300,
    )

    provided_by: PartProvidedBy

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Название запчасти не может быть пустым.")

        return value

    @field_validator("supplier")
    @classmethod
    def normalize_supplier(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class PartCreate(PartWrite):
    pass


class PartUpdate(PartWrite):
    pass


class PartResponse(BaseModel):
    part_number: int

    name: str

    quantity: int
    unit_price: Decimal
    total_price: Decimal

    supplier: str | None
    provided_by: PartProvidedBy

    @classmethod
    def from_part(cls, part) -> "PartResponse":
        total = (part.unit_price * Decimal(part.quantity)).quantize(
            _MONEY,
            rounding=ROUND_HALF_UP,
        )

        return cls(
            part_number=part.part_number,
            name=part.name,
            quantity=part.quantity,
            unit_price=part.unit_price,
            total_price=total,
            supplier=part.supplier,
            provided_by=part.provided_by,
        )


class PartListResponse(BaseModel):
    items: list[PartResponse]
    total: int

    total_price: Decimal
