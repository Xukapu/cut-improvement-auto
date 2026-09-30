from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class DisputeRecord(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Фиксация спорной ситуации внутри заказ-наряда."""

    __tablename__ = "dispute_records"
    __table_args__ = (
        Index(
            "ix_dispute_records_work_order_id",
            "work_order_id",
        ),
    )

    dispute_number: Mapped[int] = mapped_column(
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

    found_text: Mapped[str] = mapped_column(
        String(4000),
        nullable=False,
    )

    master_recommendation: Mapped[str | None] = mapped_column(
        String(4000),
        nullable=True,
    )

    client_response: Mapped[str | None] = mapped_column(
        String(4000),
        nullable=True,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class DisputePhoto(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Фотография, прикреплённая к спорной ситуации."""

    __tablename__ = "dispute_photos"
    __table_args__ = (
        Index(
            "ix_dispute_photos_dispute_id",
            "dispute_id",
        ),
    )

    photo_number: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        nullable=False,
        unique=True,
    )

    dispute_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "dispute_records.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    stored_relative_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    content_type: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
