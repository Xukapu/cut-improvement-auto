from uuid import UUID

from fastapi import APIRouter

from app.api.deps import DbSession, StaffUser
from app.schemas.sync import (
    SyncDeviceRegister,
    SyncDeviceResponse,
    SyncPushOperation,
    SyncPushResponse,
    SyncStatusResponse,
)
from app.services.sync import (
    apply_sync_operation,
    get_sync_status,
    register_sync_device,
)

router = APIRouter(
    prefix="/sync",
    tags=["sync"],
)


@router.post(
    "/devices/register",
    response_model=SyncDeviceResponse,
    summary="Зарегистрировать устройство синхронизации",
)
def register_device(
    payload: SyncDeviceRegister,
    db: DbSession,
    current_user: StaffUser,
) -> SyncDeviceResponse:
    return register_sync_device(
        db,
        user=current_user,
        payload=payload,
    )


@router.get(
    "/status/{device_key}",
    response_model=SyncStatusResponse,
    summary="Состояние устройства синхронизации",
)
def sync_status(
    device_key: UUID,
    db: DbSession,
    current_user: StaffUser,
) -> SyncStatusResponse:
    return get_sync_status(
        db,
        user=current_user,
        device_key=device_key,
    )


@router.post(
    "/push",
    response_model=SyncPushResponse,
    summary="Применить одну offline-операцию",
)
def push_operation(
    payload: SyncPushOperation,
    db: DbSession,
    current_user: StaffUser,
) -> SyncPushResponse:
    return apply_sync_operation(
        db,
        user=current_user,
        operation=payload,
    )
