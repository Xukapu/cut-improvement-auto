from datetime import datetime
from typing import Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models.client import ArchiveReason, ClientSource


class ClientWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=2, max_length=200)
    phone_primary: str = Field(min_length=5, max_length=32)
    phone_secondary: str | None = Field(default=None, max_length=32)

    source: ClientSource

    referred_by_client_number: int | None = Field(
        default=None,
        ge=1,
    )

    notes: str | None = Field(default=None, max_length=2000)

    @field_validator(
        "full_name",
        "phone_primary",
    )
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Поле не может быть пустым.")

        return value

    @field_validator(
        "phone_secondary",
        "notes",
    )
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def validate_referral(self) -> Self:
        if self.source == ClientSource.REFERRAL:
            if self.referred_by_client_number is None:
                raise ValueError(
                    "Для источника 'рекомендация' необходимо указать "
                    "номер клиента, который дал рекомендацию."
                )

        elif self.referred_by_client_number is not None:
            raise ValueError(
                "Кто рекомендовал можно указывать только для источника 'рекомендация'."
            )

        return self


class ClientCreate(ClientWrite):
    internal_mark: bool = False


class ClientUpdate(ClientWrite):
    pass


class ClientInternalMarkUpdate(BaseModel):
    internal_mark: bool


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    client_number: int

    full_name: str
    phone_primary: str
    phone_secondary: str | None

    source: ClientSource

    referred_by_client_number: int | None
    referred_by_client_name: str | None

    internal_mark: bool
    notes: str | None

    created_at: datetime
    updated_at: datetime


class ArchivedClientResponse(ClientResponse):
    archived_at: datetime
    archive_reason: ArchiveReason
    archive_comment: str | None


class ClientListResponse(BaseModel):
    items: list[ClientResponse]
    total: int
    limit: int
    offset: int


class ArchivedClientListResponse(BaseModel):
    items: list[ArchivedClientResponse]
    total: int
    limit: int
    offset: int


class ArchiveClientRequest(BaseModel):
    confirm: Literal[True]
    reason: ArchiveReason
    comment: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator("comment")
    @classmethod
    def strip_comment(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None
