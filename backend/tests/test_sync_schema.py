from uuid import uuid4

from app.schemas.sync import (
    SyncDeviceRegister,
    SyncPushOperation,
)


def test_sync_device_register_schema() -> None:
    device_key = uuid4()

    payload = SyncDeviceRegister(
        device_key=device_key,
        device_name="Ноутбук СТО",
        platform="Windows",
    )

    assert payload.device_key == device_key
    assert payload.device_name == "Ноутбук СТО"


def test_sync_client_create_operation_schema() -> None:
    operation = SyncPushOperation(
        operation_id=uuid4(),
        device_key=uuid4(),
        entity_id=uuid4(),
        kind="client.create",
        payload={
            "full_name": "Offline Client",
            "phone_primary": "+79990000000",
            "phone_secondary": None,
            "source": "other",
            "referred_by_client_id": None,
            "notes": None,
            "internal_mark": False,
        },
    )

    assert operation.kind == "client.create"


def test_sync_vehicle_create_operation_schema() -> None:
    operation = SyncPushOperation(
        operation_id=uuid4(),
        device_key=uuid4(),
        entity_id=uuid4(),
        kind="vehicle.create",
        payload={
            "license_plate": "A123BC77",
            "vin": None,
            "brand": "Volkswagen",
            "model": "Polo",
            "year": 2020,
            "mileage": 50000,
            "owner_client_id": str(uuid4()),
        },
    )

    assert operation.kind == "vehicle.create"


def test_sync_appointment_create_operation_schema() -> None:
    operation = SyncPushOperation(
        operation_id=uuid4(),
        device_key=uuid4(),
        entity_id=uuid4(),
        kind="appointment.create",
        payload={
            "client_id": str(uuid4()),
            "vehicle_id": str(uuid4()),
            "appointment_date": "2026-10-02",
            "appointment_time": "12:00",
            "reason": "Диагностика",
            "comment": None,
            "status": "scheduled",
        },
    )

    assert operation.kind == "appointment.create"
