from datetime import date
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Index, true
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class ClientVehicle(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """История владения автомобилем клиентом."""

    __tablename__ = "client_vehicles"
    __table_args__ = (
        CheckConstraint(
            "ended_at IS NULL OR started_at IS NULL OR ended_at >= started_at",
            name="ownership_dates_valid",
        ),
        Index(
            "ix_client_vehicles_client_vehicle",
            "client_id",
            "vehicle_id",
        ),
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

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    started_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    ended_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
