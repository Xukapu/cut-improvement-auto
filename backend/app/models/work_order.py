from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class WorkOrderStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    ISSUED = "issued"


class WorkOrder(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Заказ-наряд СТО."""

    __tablename__ = "work_orders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('planned', 'in_progress', 'ready', 'issued')",
            name="status_valid",
        ),
        CheckConstraint(
            "mileage IS NULL OR mileage >= 0",
            name="mileage_non_negative",
        ),
        CheckConstraint(
            "(status <> 'issued') OR (issued_at IS NOT NULL)",
            name="issued_requires_date",
        ),
        Index(
            "ix_work_orders_client_id",
            "client_id",
        ),
        Index(
            "ix_work_orders_vehicle_id",
            "vehicle_id",
        ),
        Index(
            "ix_work_orders_status",
            "status",
        ),
        Index(
            "ix_work_orders_created_at",
            "created_at",
        ),
    )

    work_order_number: Mapped[int] = mapped_column(
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

    appointment_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "appointments.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        unique=True,
    )

    status: Mapped[WorkOrderStatus] = mapped_column(
        SQLEnum(
            WorkOrderStatus,
            name="work_order_status",
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
            length=32,
        ),
        nullable=False,
        default=WorkOrderStatus.PLANNED,
        server_default=WorkOrderStatus.PLANNED.value,
    )

    reason: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    mileage: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    ready_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    issued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
