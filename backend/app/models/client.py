from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    false,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class ClientSource(StrEnum):
    AVITO = "avito"
    REFERRAL = "referral"
    OTHER = "other"


class ArchiveReason(StrEnum):
    NO_LONGER_SERVICED = "no_longer_serviced"
    CREATED_BY_MISTAKE = "created_by_mistake"
    OWNER_REQUEST = "owner_request"
    OTHER = "other"


class Client(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Клиент СТО."""

    __tablename__ = "clients"
    __table_args__ = (
        CheckConstraint(
            "source IN ('avito', 'referral', 'other')",
            name="source_valid",
        ),
        CheckConstraint(
            "("
            "source = 'referral' AND referred_by_client_id IS NOT NULL"
            ") OR ("
            "source <> 'referral' AND referred_by_client_id IS NULL"
            ")",
            name="referral_matches_source",
        ),
        CheckConstraint(
            "referred_by_client_id IS NULL OR referred_by_client_id <> id",
            name="cannot_refer_self",
        ),
        CheckConstraint(
            "archive_reason IS NULL OR archive_reason IN ("
            "'no_longer_serviced', "
            "'created_by_mistake', "
            "'owner_request', "
            "'other'"
            ")",
            name="archive_reason_valid",
        ),
        CheckConstraint(
            "("
            "archived_at IS NULL "
            "AND archive_reason IS NULL "
            "AND archive_comment IS NULL "
            "AND archived_by_user_id IS NULL"
            ") OR ("
            "archived_at IS NOT NULL "
            "AND archive_reason IS NOT NULL "
            "AND archived_by_user_id IS NOT NULL"
            ")",
            name="archive_state_consistent",
        ),
        Index("ix_clients_full_name", "full_name"),
        Index("ix_clients_phone_primary", "phone_primary"),
        Index("ix_clients_archived_at", "archived_at"),
    )

    client_number: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        nullable=False,
        unique=True,
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

    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    archive_reason: Mapped[ArchiveReason | None] = mapped_column(
        SQLEnum(
            ArchiveReason,
            name="client_archive_reason",
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
            length=32,
        ),
        nullable=True,
    )

    archive_comment: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    archived_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "app_users.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    referred_by: Mapped["Client | None"] = relationship(
        "Client",
        remote_side="Client.id",
        foreign_keys=[referred_by_client_id],
        lazy="joined",
    )

    @property
    def referred_by_client_number(self) -> int | None:
        if self.referred_by is None:
            return None

        return self.referred_by.client_number

    @property
    def referred_by_client_name(self) -> str | None:
        if self.referred_by is None:
            return None

        return self.referred_by.full_name
