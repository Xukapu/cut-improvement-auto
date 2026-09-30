from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Identity,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class Vehicle(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Автомобиль."""

    __tablename__ = "vehicles"
    __table_args__ = (
        CheckConstraint(
            "year IS NULL OR year BETWEEN 1886 AND 2100",
            name="year_valid",
        ),
        CheckConstraint(
            "mileage IS NULL OR mileage >= 0",
            name="mileage_non_negative",
        ),
        Index("ix_vehicles_license_plate", "license_plate"),
        Index("ix_vehicles_vin", "vin"),
        Index("ix_vehicles_brand_model", "brand", "model"),
    )

    vehicle_number: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        nullable=False,
        unique=True,
    )

    license_plate: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    vin: Mapped[str | None] = mapped_column(
        String(17),
        nullable=True,
        unique=True,
    )

    brand: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    mileage: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
