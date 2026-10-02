from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

SyncOperationKind = Literal[
    "client.create",
    "vehicle.create",
    "appointment.create",
]


class SyncDeviceRegister(BaseModel):
    device_key: UUID

    device_name: str = Field(
        min_length=1,
        max_length=120,
    )

    platform: str = Field(
        min_length=1,
        max_length=200,
    )


class SyncDeviceResponse(BaseModel):
    device_key: UUID
    device_name: str
    platform: str
    last_seen_at: datetime
    last_sync_at: datetime | None


class SyncStatusResponse(BaseModel):
    server_time: datetime
    device_registered: bool
    device: SyncDeviceResponse | None


class SyncPushOperation(BaseModel):
    operation_id: UUID
    device_key: UUID
    entity_id: UUID
    kind: SyncOperationKind
    payload: dict[str, Any]


class SyncPushResponse(BaseModel):
    operation_id: UUID
    entity_id: UUID
    kind: SyncOperationKind

    result_number: int

    replayed: bool
    server_time: datetime
