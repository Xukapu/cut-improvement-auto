from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    false,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class ClientSource(StrEnum):
    AVITO = "avito"
    REFERRAL = "referral"
    OTHER = "other"


class Client(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Клиент СТО."""

    __tablename__ = "clients"
    __table_args__ = (
        CheckConstraint(
            "source IN ('avito', 'referral', 'other')",
            name="source_valid",
        ),
        Index("ix_clients_full_name", "full_name"),
        Index("ix_clients_phone_primary", "phone_primary"),
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    phone_primary: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    phone_secondary: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    source: Mapped[ClientSource] = mapped_column(
        SQLEnum(
            ClientSource,
            name="client_source",
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
            length=32,
        ),
        nullable=False,
    )

    referred_by_client_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "clients.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    internal_mark: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )

    notes: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
