from uuid import uuid4

from app.schemas.sync import (
    SyncDeviceRegister,
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
