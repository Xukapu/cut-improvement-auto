from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    String,
    func,
    text,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class Employee(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Сотрудник СТО."""

    __tablename__ = "employees"

    employee_number: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        nullable=False,
        unique=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )


class EmployeeRate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """История процентных ставок сотрудника."""

    __tablename__ = "employee_rates"
    __table_args__ = (
        CheckConstraint(
            "rate_percent >= 0 AND rate_percent <= 100",
            name="rate_percent_valid",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="effective_dates_valid",
        ),
        Index(
            "ix_employee_rates_employee_id",
            "employee_id",
        ),
        Index(
            "uq_employee_rates_current",
            "employee_id",
            unique=True,
            postgresql_where=text("effective_to IS NULL"),
        ),
    )

    employee_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "employees.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    rate_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    effective_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
