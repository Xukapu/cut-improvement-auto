from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DisputeWrite(BaseModel):
    found_text: str = Field(
        min_length=2,
        max_length=4000,
    )

    master_recommendation: str | None = Field(
        default=None,
        max_length=4000,
    )

    client_response: str | None = Field(
        default=None,
        max_length=4000,
    )

    @field_validator("found_text")
    @classmethod
    def normalize_found_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Описание обнаруженного не может быть пустым.")

        return value

    @field_validator(
        "master_recommendation",
        "client_response",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class DisputeCreate(DisputeWrite):
    pass


class DisputeUpdate(DisputeWrite):
    pass


class DisputeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dispute_number: int

    found_text: str
    master_recommendation: str | None
    client_response: str | None

    recorded_at: datetime


class DisputeListResponse(BaseModel):
    items: list[DisputeResponse]
    total: int


class DisputePhotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    photo_number: int
    original_filename: str
    content_type: str | None
    size_bytes: int


class DisputePhotoListResponse(BaseModel):
    items: list[DisputePhotoResponse]
    total: int
