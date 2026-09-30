from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_number: int

    actor_login: str | None
    actor_role: str | None

    action: str

    entity_type: str
    entity_number: int | None

    old_values: dict[str, Any] | None
    new_values: dict[str, Any] | None

    created_at: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]

    total: int
    limit: int
    offset: int
