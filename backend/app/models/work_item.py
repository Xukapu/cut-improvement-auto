from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class WorkItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Р Р°Р±РѕС‚Р° РІРЅСѓС‚СЂРё Р·Р°РєР°Р·-РЅР°СЂСЏРґР°."""

    __tablename__ = "work_items"
    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name="price_non_negative",
        ),
        Index(
            "ix_work_items_work_order_id",
            "work_order_id",
        ),
    )

    work_item_number: Mapped[int] = mapped_column(
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

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )


class WorkItemAssignment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Р”РѕР»СЏ СЃРѕС‚СЂСѓРґРЅРёРєР° РІ РєРѕРЅРєСЂРµС‚РЅРѕР№ СЂР°Р±РѕС‚Рµ."""

    __tablename__ = "work_item_assignments"
    __table_args__ = (
        CheckConstraint(
            "share_percent > 0 AND share_percent <= 100",
            name="share_percent_valid",
        ),
        CheckConstraint(
            "rate_percent_snapshot >= 0 AND rate_percent_snapshot <= 100",
            name="rate_snapshot_valid",
        ),
        UniqueConstraint(
            "work_item_id",
            "employee_id",
            name="uq_work_item_assignments_work_item_employee",
        ),
        Index(
            "ix_work_item_assignments_work_item_id",
            "work_item_id",
        ),
        Index(
            "ix_work_item_assignments_employee_id",
            "employee_id",
        ),
    )

    work_item_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "work_items.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    employee_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "employees.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    share_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    rate_percent_snapshot: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )
