from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.repositories.appointment import get_appointment_by_number
from app.repositories.client import get_client_by_number
from app.repositories.vehicle import (
    get_current_ownership,
    get_vehicle_by_number,
)
from app.repositories.work_order import (
    get_work_order_by_appointment_id,
    get_work_order_by_number,
    get_work_order_details,
)
from app.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderResponse,
    WorkOrderUpdate,
)

_ALLOWED_STATUS_TRANSITIONS: dict[
    WorkOrderStatus,
    frozenset[WorkOrderStatus],
] = {
    WorkOrderStatus.PLANNED: frozenset(
        {
            WorkOrderStatus.IN_PROGRESS,
        }
    ),
    WorkOrderStatus.IN_PROGRESS: frozenset(
        {
            WorkOrderStatus.READY,
        }
    ),
    WorkOrderStatus.READY: frozenset(
        {
            WorkOrderStatus.IN_PROGRESS,
            WorkOrderStatus.ISSUED,
        }
    ),
    WorkOrderStatus.ISSUED: frozenset(),
}


def validate_client_vehicle(
    db: Session,
    *,
    client_number: int,
    vehicle_number: int,
):
    client = get_client_by_number(
        db,
        client_number,
    )

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Активный клиент не найден.",
        )

    vehicle = get_vehicle_by_number(
        db,
        vehicle_number,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Автомобиль не найден.",
        )

    ownership = get_current_ownership(
        db,
        vehicle.id,
    )

    if ownership is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="У автомобиля отсутствует текущий владелец.",
        )

    _ownership, owner = ownership

    if owner.id != client.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("Указанный автомобиль не принадлежит этому клиенту."),
        )

    return client, vehicle


def validate_appointment(
    db: Session,
    *,
    appointment_number: int | None,
    client_id,
    vehicle_id,
) -> Appointment | None:
    if appointment_number is None:
        return None

    appointment = get_appointment_by_number(
        db,
        appointment_number,
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Указанная запись не найдена.",
        )

    if appointment.client_id != client_id or appointment.vehicle_id != vehicle_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("Запись относится к другому клиенту или автомобилю."),
        )

    existing_order = get_work_order_by_appointment_id(
        db,
        appointment.id,
    )

    if existing_order is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(f"Для этой записи уже создан заказ-наряд №{existing_order.work_order_number}."),
        )

    return appointment


def build_work_order_response(
    order: WorkOrder,
    *,
    client,
    vehicle,
    appointment: Appointment | None,
) -> WorkOrderResponse:
    return WorkOrderResponse(
        work_order_number=order.work_order_number,
        client_number=client.client_number,
        client_name=client.full_name,
        vehicle_number=vehicle.vehicle_number,
        license_plate=vehicle.license_plate,
        appointment_number=(appointment.appointment_number if appointment is not None else None),
        status=order.status,
        reason=order.reason,
        mileage=order.mileage,
        created_at=order.created_at,
        started_at=order.started_at,
        ready_at=order.ready_at,
        issued_at=order.issued_at,
    )


def get_work_order_response(
    db: Session,
    order: WorkOrder,
) -> WorkOrderResponse:
    details = get_work_order_details(
        db,
        order.id,
    )

    if details is None:
        raise RuntimeError("Не удалось получить данные заказ-наряда.")

    _order, client, vehicle, appointment = details

    return build_work_order_response(
        order,
        client=client,
        vehicle=vehicle,
        appointment=appointment,
    )


def create_work_order(
    db: Session,
    payload: WorkOrderCreate,
) -> WorkOrderResponse:
    client, vehicle = validate_client_vehicle(
        db,
        client_number=payload.client_number,
        vehicle_number=payload.vehicle_number,
    )

    appointment = validate_appointment(
        db,
        appointment_number=payload.appointment_number,
        client_id=client.id,
        vehicle_id=vehicle.id,
    )

    order = WorkOrder(
        client_id=client.id,
        vehicle_id=vehicle.id,
        appointment_id=(appointment.id if appointment is not None else None),
        status=WorkOrderStatus.PLANNED,
        reason=payload.reason,
        mileage=payload.mileage,
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return build_work_order_response(
        order,
        client=client,
        vehicle=vehicle,
        appointment=appointment,
    )


def update_work_order(
    db: Session,
    *,
    order: WorkOrder,
    payload: WorkOrderUpdate,
) -> WorkOrderResponse:
    if order.status == WorkOrderStatus.ISSUED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Выданный заказ-наряд нельзя редактировать."),
        )

    order.reason = payload.reason
    order.mileage = payload.mileage

    db.commit()
    db.refresh(order)

    return get_work_order_response(
        db,
        order,
    )


def change_work_order_status(
    db: Session,
    *,
    order: WorkOrder,
    new_status: WorkOrderStatus,
) -> WorkOrderResponse:
    if new_status == order.status:
        return get_work_order_response(
            db,
            order,
        )

    allowed = _ALLOWED_STATUS_TRANSITIONS[order.status]

    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(f"Недопустимый переход статуса: {order.status.value} -> {new_status.value}."),
        )

    now = datetime.now(UTC)

    if new_status == WorkOrderStatus.IN_PROGRESS:
        if order.started_at is None:
            order.started_at = now

        if order.status == WorkOrderStatus.READY:
            order.ready_at = None

    elif new_status == WorkOrderStatus.READY:
        order.ready_at = now

    elif new_status == WorkOrderStatus.ISSUED:
        order.issued_at = now

    order.status = new_status

    db.commit()
    db.refresh(order)

    return get_work_order_response(
        db,
        order,
    )


def require_work_order(
    db: Session,
    work_order_number: int,
) -> WorkOrder:
    order = get_work_order_by_number(
        db,
        work_order_number,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ-наряд не найден.",
        )

    return order
