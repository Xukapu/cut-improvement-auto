from datetime import date, time
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    ForeignKey,
    Identity,
    Index,
    String,
    Time,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class AppointmentStatus(StrEnum):
    SCHEDULED = "scheduled"
    NO_SHOW = "no_show"


class Appointment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Запись клиента на обслуживание."""

    __tablename__ = "appointments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'no_show')",
            name="status_valid",
        ),
        Index(
            "ix_appointments_date_time",
            "appointment_date",
            "appointment_time",
        ),
        Index(
            "ix_appointments_client_id",
            "client_id",
        ),
        Index(
            "ix_appointments_vehicle_id",
            "vehicle_id",
        ),
    )

    appointment_number: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        nullable=False,
        unique=True,
    )

    client_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "clients.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    vehicle_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "vehicles.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    appointment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    appointment_time: Mapped[time] = mapped_column(
        Time(timezone=False),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    comment: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(
            AppointmentStatus,
            name="appointment_status",
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
            length=32,
        ),
        nullable=False,
        default=AppointmentStatus.SCHEDULED,
        server_default=AppointmentStatus.SCHEDULED.value,
    )
