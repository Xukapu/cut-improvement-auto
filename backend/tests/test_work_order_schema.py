import pytest
from app.models.work_order import WorkOrderStatus
from app.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderStatusUpdate,
)
from pydantic import ValidationError


def test_work_order_create() -> None:
    order = WorkOrderCreate(
        client_number=2,
        vehicle_number=1,
        appointment_number=1,
        reason="Замена масла",
        mileage=55000,
    )

    assert order.client_number == 2
    assert order.vehicle_number == 1
    assert order.appointment_number == 1


def test_work_order_reason_is_trimmed() -> None:
    order = WorkOrderCreate(
        client_number=2,
        vehicle_number=1,
        reason="  Замена масла  ",
    )

    assert order.reason == "Замена масла"


def test_negative_mileage_is_rejected() -> None:
    with pytest.raises(ValidationError):
        WorkOrderCreate(
            client_number=2,
            vehicle_number=1,
            reason="Диагностика",
            mileage=-1,
        )


def test_work_order_numbers_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        WorkOrderCreate(
            client_number=0,
            vehicle_number=1,
            reason="Диагностика",
        )


def test_status_update_accepts_known_status() -> None:
    payload = WorkOrderStatusUpdate(
        status=WorkOrderStatus.IN_PROGRESS,
    )

    assert payload.status == WorkOrderStatus.IN_PROGRESS
