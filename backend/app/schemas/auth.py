from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.security import normalize_login
from app.models.user import UserRole


class LoginRequest(BaseModel):
    login: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("login")
    @classmethod
    def validate_login(cls, value: str) -> str:
        return normalize_login(value)


class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    login: str
    role: UserRole


class MessageResponse(BaseModel):
    message: str
