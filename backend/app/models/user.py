from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    text,
    true,
)
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
        CheckConstraint(
            "failed_login_attempts >= 0",
            name="failed_login_attempts_non_negative",
        ),
        CheckConstraint(
            "login = lower(login)",
            name="login_lowercase",
        ),
        Index("ix_app_users_role", "role"),
        Index("ix_app_users_phone", "phone"),
        Index(
            "uq_app_users_employee_id",
            "employee_id",
            unique=True,
        ),
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    first_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    employee_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "employees.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
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
            values_callable=lambda enum_type: [
                item.value
                for item in enum_type
            ],
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

    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    password_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )