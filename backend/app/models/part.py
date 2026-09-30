from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class PartProvidedBy(StrEnum):
    STO = "sto"
    CLIENT = "client"


class Part(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Запчасть внутри заказ-наряда."""

    __tablename__ = "parts"
    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name="price_non_negative",
        ),
        CheckConstraint(
            "quantity > 0",
            name="quantity_positive",
        ),
        CheckConstraint(
            "provided_by IN ('sto', 'client')",
            name="provided_by_valid",
        ),
        Index(
            "ix_parts_work_order_id",
            "work_order_id",
        ),
    )

    part_number: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        nullable=False,
        unique=True,
    )

    work_order_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "work_orders.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    unit_price: Mapped[Decimal] = mapped_column(
        "price",
        Numeric(12, 2),
        nullable=False,
    )

    supplier: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    provided_by: Mapped[PartProvidedBy] = mapped_column(
        SQLEnum(
            PartProvidedBy,
            name="part_provided_by",
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
            length=32,
        ),
        nullable=False,
    )
