from uuid import UUID

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Identity,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class RecommendedWork(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Работа, рекомендованная клиенту, но не выполненная."""

    __tablename__ = "recommended_works"
    __table_args__ = (
        Index(
            "ix_recommended_works_work_order_id",
            "work_order_id",
        ),
    )

    recommended_work_number: Mapped[int] = mapped_column(
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

    comment: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
