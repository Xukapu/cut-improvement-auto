from enum import StrEnum

from sqlalchemy import Boolean, CheckConstraint, Index, String, true
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MECHANIC = "mechanic"
    TECH_ADMIN = "tech_admin"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Пользователь веб-приложения."""

    __tablename__ = "app_users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('owner', 'admin', 'mechanic', 'tech_admin')",
            name="role_valid",
        ),
        Index("ix_app_users_role", "role"),
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    login: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(
            UserRole,
            name="user_role",
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
            length=32,
        ),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )
