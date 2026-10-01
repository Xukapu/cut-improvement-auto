from decimal import Decimal
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from app.core.security import normalize_login
from app.models.user import UserRole


def _clean_text(
    value: str,
) -> str:
    return " ".join(value.strip().split())


def _clean_optional(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    cleaned = " ".join(value.strip().split())

    return cleaned or None


def _validate_assignable_role(
    value: UserRole | None,
) -> UserRole | None:
    if value == UserRole.TECH_ADMIN:
        raise ValueError(
            "Технический администратор — служебная роль "
            "и не назначается через интерфейс сотрудников."
        )

    return value


class ProfileResponse(BaseModel):
    first_name: str
    last_name: str
    phone: str | None
    login: str
    role: UserRole
    full_name: str


class ProfileUpdate(BaseModel):
    first_name: str = Field(
        min_length=1,
        max_length=100,
    )

    last_name: str = Field(
        min_length=1,
        max_length=100,
    )

    phone: str = Field(
        min_length=5,
        max_length=32,
    )

    @field_validator(
        "first_name",
        "last_name",
        "phone",
    )
    @classmethod
    def clean_fields(
        cls,
        value: str,
    ) -> str:
        return _clean_text(value)


class PasswordChange(BaseModel):
    current_password: str = Field(
        min_length=1,
        max_length=128,
    )

    new_password: str = Field(
        min_length=12,
        max_length=128,
    )


class EmployeeAccessCreate(BaseModel):
    full_name: str = Field(
        min_length=1,
        max_length=200,
    )

    rate_percent: Decimal = Field(
        ge=0,
        le=100,
        decimal_places=2,
    )

    grant_access: bool = False

    login: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )

    role: UserRole = UserRole.MECHANIC

    temporary_password: str | None = Field(
        default=None,
        min_length=12,
        max_length=128,
    )

    phone: str | None = Field(
        default=None,
        max_length=32,
    )

    @field_validator("full_name")
    @classmethod
    def clean_name(
        cls,
        value: str,
    ) -> str:
        return _clean_text(value)

    @field_validator("login")
    @classmethod
    def clean_login(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return normalize_login(value)

    @field_validator("phone")
    @classmethod
    def clean_phone(
        cls,
        value: str | None,
    ) -> str | None:
        return _clean_optional(value)

    @field_validator("role")
    @classmethod
    def validate_role(
        cls,
        value: UserRole,
    ) -> UserRole:
        result = _validate_assignable_role(value)

        assert result is not None
        return result

    @model_validator(mode="after")
    def validate_access(
        self,
    ) -> "EmployeeAccessCreate":
        if not self.grant_access:
            return self

        if not self.login:
            raise ValueError("Для доступа к системе укажите логин.")

        if not self.temporary_password:
            raise ValueError("Для нового доступа укажите временный пароль.")

        return self


class EmployeeAccessUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    rate_percent: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        decimal_places=2,
    )

    is_active: bool | None = None
    grant_access: bool | None = None

    login: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )

    role: UserRole | None = None

    phone: str | None = Field(
        default=None,
        max_length=32,
    )

    temporary_password: str | None = Field(
        default=None,
        min_length=12,
        max_length=128,
    )

    @field_validator("full_name")
    @classmethod
    def clean_name(
        cls,
        value: str | None,
    ) -> str | None:
        return _clean_optional(value)

    @field_validator("login")
    @classmethod
    def clean_login(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return normalize_login(value)

    @field_validator("phone")
    @classmethod
    def clean_phone(
        cls,
        value: str | None,
    ) -> str | None:
        return _clean_optional(value)

    @field_validator("role")
    @classmethod
    def validate_role(
        cls,
        value: UserRole | None,
    ) -> UserRole | None:
        return _validate_assignable_role(value)


class EmployeePasswordReset(BaseModel):
    new_password: str = Field(
        min_length=12,
        max_length=128,
    )


class EmployeeAccessResponse(BaseModel):
    employee_number: int
    full_name: str

    is_active: bool
    archived: bool

    current_rate_percent: Decimal

    access_exists: bool
    access_enabled: bool

    user_id: UUID | None = None
    login: str | None = None
    role: UserRole | None = None
    phone: str | None = None
