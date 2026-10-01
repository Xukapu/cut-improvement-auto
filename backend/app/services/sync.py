from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sync import SyncDevice
from app.models.user import User
from app.schemas.sync import (
    SyncDeviceRegister,
    SyncDeviceResponse,
    SyncStatusResponse,
)


def sync_device_response(
    device: SyncDevice,
) -> SyncDeviceResponse:
    return SyncDeviceResponse(
        device_key=device.device_key,
        device_name=device.device_name,
        platform=device.platform,
        last_seen_at=device.last_seen_at,
        last_sync_at=device.last_sync_at,
    )


def register_sync_device(
    db: Session,
    *,
    user: User,
    payload: SyncDeviceRegister,
) -> SyncDeviceResponse:
    device = db.scalar(
        select(SyncDevice).where(
            SyncDevice.user_id == user.id,
            SyncDevice.device_key == payload.device_key,
            SyncDevice.deleted_at.is_(None),
        )
    )

    now = datetime.now(UTC)

    if device is None:
        device = SyncDevice(
            user_id=user.id,
            device_key=payload.device_key,
            device_name=(payload.device_name),
            platform=payload.platform,
            last_seen_at=now,
        )

        db.add(device)
    else:
        device.device_name = payload.device_name

        device.platform = payload.platform

        device.last_seen_at = now

    db.commit()
    db.refresh(device)

    return sync_device_response(device)


def get_sync_status(
    db: Session,
    *,
    user: User,
    device_key: UUID,
) -> SyncStatusResponse:
    device = db.scalar(
        select(SyncDevice).where(
            SyncDevice.user_id == user.id,
            SyncDevice.device_key == device_key,
            SyncDevice.deleted_at.is_(None),
        )
    )

    return SyncStatusResponse(
        server_time=datetime.now(UTC),
        device_registered=(device is not None),
        device=(sync_device_response(device) if device is not None else None),
    )
