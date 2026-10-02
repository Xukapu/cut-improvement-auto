from datetime import UTC, date, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.client import Client
from app.models.client_vehicle import ClientVehicle
from app.models.sync import SyncDevice, SyncOperation
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle
from app.repositories.vehicle import (
    get_current_ownership,
    get_vehicle_by_vin,
)
from app.schemas.appointment import AppointmentCreate
from app.schemas.client import ClientCreate
from app.schemas.sync import (
    SyncDeviceRegister,
    SyncDeviceResponse,
    SyncPushOperation,
    SyncPushResponse,
    SyncStatusResponse,
)
from app.schemas.vehicle import VehicleCreate


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
            device_name=payload.device_name,
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
        device_registered=device is not None,
        device=(sync_device_response(device) if device is not None else None),
    )


def _require_device(
    db: Session,
    *,
    user: User,
    device_key: UUID,
) -> SyncDevice:
    device = db.scalar(
        select(SyncDevice).where(
            SyncDevice.user_id == user.id,
            SyncDevice.device_key == device_key,
            SyncDevice.deleted_at.is_(None),
        )
    )

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Устройство синхронизации не зарегистрировано.",
        )

    return device


def _require_role(
    user: User,
    allowed: set[UserRole],
) -> None:
    if user.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для этой offline-операции.",
        )


def _existing_operation(
    db: Session,
    *,
    user: User,
    operation_id: UUID,
) -> SyncOperation | None:
    return db.scalar(
        select(SyncOperation).where(
            SyncOperation.user_id == user.id,
            SyncOperation.operation_id == operation_id,
            SyncOperation.deleted_at.is_(None),
        )
    )


def _response(
    *,
    operation: SyncPushOperation,
    result_number: int,
    replayed: bool,
) -> SyncPushResponse:
    return SyncPushResponse(
        operation_id=operation.operation_id,
        entity_id=operation.entity_id,
        kind=operation.kind,
        result_number=result_number,
        replayed=replayed,
        server_time=datetime.now(UTC),
    )


def _create_client(
    db: Session,
    *,
    user: User,
    operation: SyncPushOperation,
) -> int:
    _require_role(
        user,
        {
            UserRole.OWNER,
            UserRole.TECH_ADMIN,
            UserRole.ADMIN,
        },
    )

    existing = db.get(
        Client,
        operation.entity_id,
    )

    if existing is not None:
        return existing.client_number

    raw = dict(operation.payload)

    referred_by_client_id = raw.pop(
        "referred_by_client_id",
        None,
    )

    referrer = None

    if referred_by_client_id is not None:
        try:
            referrer_uuid = UUID(str(referred_by_client_id))
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Некорректный UUID рекомендателя.",
            ) from error

        referrer = db.get(
            Client,
            referrer_uuid,
        )

        if referrer is None or referrer.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=("Клиент-рекомендатель ещё не синхронизирован или больше не активен."),
            )

        raw["referred_by_client_number"] = referrer.client_number
    else:
        raw["referred_by_client_number"] = None

    payload = ClientCreate.model_validate(raw)

    if payload.internal_mark and user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=("Внутреннюю метку клиента может устанавливать только владелец."),
        )

    data = payload.model_dump(
        exclude={
            "referred_by_client_number",
        }
    )

    client = Client(
        id=operation.entity_id,
        **data,
        referred_by_client_id=(referrer.id if referrer is not None else None),
    )

    db.add(client)
    db.flush()

    return client.client_number


def _create_vehicle(
    db: Session,
    *,
    user: User,
    operation: SyncPushOperation,
) -> int:
    _require_role(
        user,
        {
            UserRole.OWNER,
            UserRole.TECH_ADMIN,
            UserRole.ADMIN,
        },
    )

    existing = db.get(
        Vehicle,
        operation.entity_id,
    )

    if existing is not None:
        return existing.vehicle_number

    raw = dict(operation.payload)

    owner_client_id = raw.pop(
        "owner_client_id",
        None,
    )

    if owner_client_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Не указан UUID владельца автомобиля.",
        )

    try:
        owner_uuid = UUID(str(owner_client_id))
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Некорректный UUID владельца.",
        ) from error

    owner = db.get(
        Client,
        owner_uuid,
    )

    if owner is None or owner.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Владелец автомобиля ещё не синхронизирован или больше не активен."),
        )

    raw["owner_client_number"] = owner.client_number

    payload = VehicleCreate.model_validate(raw)

    if payload.vin is not None:
        same_vin = get_vehicle_by_vin(
            db,
            payload.vin,
        )

        if same_vin is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Автомобиль с таким VIN уже существует.",
            )

    vehicle = Vehicle(
        id=operation.entity_id,
        license_plate=payload.license_plate,
        vin=payload.vin,
        brand=payload.brand,
        model=payload.model,
        year=payload.year,
        mileage=payload.mileage,
    )

    db.add(vehicle)
    db.flush()

    ownership = ClientVehicle(
        client_id=owner.id,
        vehicle_id=vehicle.id,
        is_current=True,
        started_at=date.today(),
    )

    db.add(ownership)
    db.flush()

    return vehicle.vehicle_number


def _create_appointment(
    db: Session,
    *,
    user: User,
    operation: SyncPushOperation,
) -> int:
    _require_role(
        user,
        {
            UserRole.OWNER,
            UserRole.TECH_ADMIN,
        },
    )

    existing = db.get(
        Appointment,
        operation.entity_id,
    )

    if existing is not None:
        return existing.appointment_number

    raw = dict(operation.payload)

    client_id = raw.pop(
        "client_id",
        None,
    )

    vehicle_id = raw.pop(
        "vehicle_id",
        None,
    )

    if client_id is None or vehicle_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Не указаны UUID клиента или автомобиля.",
        )

    try:
        client_uuid = UUID(str(client_id))

        vehicle_uuid = UUID(str(vehicle_id))
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Некорректный UUID клиента или автомобиля.",
        ) from error

    client = db.get(
        Client,
        client_uuid,
    )

    vehicle = db.get(
        Vehicle,
        vehicle_uuid,
    )

    if client is None or client.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Клиент ещё не синхронизирован или больше не активен.",
        )

    if vehicle is None or vehicle.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Автомобиль ещё не синхронизирован или больше не активен.",
        )

    ownership = get_current_ownership(
        db,
        vehicle.id,
    )

    if ownership is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="У автомобиля отсутствует текущий владелец.",
        )

    _ownership_record, current_owner = ownership

    if current_owner.id != client.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Автомобиль не принадлежит выбранному клиенту.",
        )

    raw["client_number"] = client.client_number

    raw["vehicle_number"] = vehicle.vehicle_number

    payload = AppointmentCreate.model_validate(raw)

    appointment = Appointment(
        id=operation.entity_id,
        client_id=client.id,
        vehicle_id=vehicle.id,
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
        reason=payload.reason,
        comment=payload.comment,
        status=payload.status,
    )

    db.add(appointment)
    db.flush()

    return appointment.appointment_number


def apply_sync_operation(
    db: Session,
    *,
    user: User,
    operation: SyncPushOperation,
) -> SyncPushResponse:
    device = _require_device(
        db,
        user=user,
        device_key=operation.device_key,
    )

    previous = _existing_operation(
        db,
        user=user,
        operation_id=operation.operation_id,
    )

    if previous is not None:
        return _response(
            operation=operation,
            result_number=previous.result_number,
            replayed=True,
        )

    if operation.kind == "client.create":
        result_number = _create_client(
            db,
            user=user,
            operation=operation,
        )

    elif operation.kind == "vehicle.create":
        result_number = _create_vehicle(
            db,
            user=user,
            operation=operation,
        )

    elif operation.kind == "appointment.create":
        result_number = _create_appointment(
            db,
            user=user,
            operation=operation,
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неизвестный тип sync-операции.",
        )

    now = datetime.now(UTC)

    receipt = SyncOperation(
        operation_id=operation.operation_id,
        device_id=device.id,
        user_id=user.id,
        operation_kind=operation.kind,
        entity_id=operation.entity_id,
        result_number=result_number,
        applied_at=now,
    )

    db.add(receipt)

    device.last_seen_at = now
    device.last_sync_at = now

    db.commit()

    return _response(
        operation=operation,
        result_number=result_number,
        replayed=False,
    )
