from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.client import Client
from app.models.vehicle import Vehicle
from app.models.work_order import WorkOrder, WorkOrderStatus


def get_work_order_by_number(
    db: Session,
    work_order_number: int,
) -> WorkOrder | None:
    return db.scalar(
        select(WorkOrder).where(
            WorkOrder.work_order_number == work_order_number,
            WorkOrder.deleted_at.is_(None),
        )
    )


def get_work_order_by_appointment_id(
    db: Session,
    appointment_id,
) -> WorkOrder | None:
    return db.scalar(
        select(WorkOrder).where(
            WorkOrder.appointment_id == appointment_id,
            WorkOrder.deleted_at.is_(None),
        )
    )


def get_work_order_details(
    db: Session,
    work_order_id,
) -> (
    tuple[
        WorkOrder,
        Client,
        Vehicle,
        Appointment | None,
    ]
    | None
):
    row = db.execute(
        select(
            WorkOrder,
            Client,
            Vehicle,
            Appointment,
        )
        .join(
            Client,
            Client.id == WorkOrder.client_id,
        )
        .join(
            Vehicle,
            Vehicle.id == WorkOrder.vehicle_id,
        )
        .outerjoin(
            Appointment,
            Appointment.id == WorkOrder.appointment_id,
        )
        .where(
            WorkOrder.id == work_order_id,
            WorkOrder.deleted_at.is_(None),
        )
    ).first()

    if row is None:
        return None

    return row[0], row[1], row[2], row[3]


def list_work_orders(
    db: Session,
    *,
    status: WorkOrderStatus | None,
    client_number: int | None,
    vehicle_number: int | None,
    limit: int,
    offset: int,
) -> tuple[
    list[
        tuple[
            WorkOrder,
            Client,
            Vehicle,
            Appointment | None,
        ]
    ],
    int,
]:
    filters = [
        WorkOrder.deleted_at.is_(None),
    ]

    if status is not None:
        filters.append(WorkOrder.status == status)

    if client_number is not None:
        filters.append(Client.client_number == client_number)

    if vehicle_number is not None:
        filters.append(Vehicle.vehicle_number == vehicle_number)

    query = (
        select(
            WorkOrder,
            Client,
            Vehicle,
            Appointment,
        )
        .join(
            Client,
            Client.id == WorkOrder.client_id,
        )
        .join(
            Vehicle,
            Vehicle.id == WorkOrder.vehicle_id,
        )
        .outerjoin(
            Appointment,
            Appointment.id == WorkOrder.appointment_id,
        )
        .where(*filters)
    )

    total = db.scalar(select(func.count()).select_from(query.subquery()))

    rows = db.execute(
        query.order_by(
            WorkOrder.created_at.desc(),
            WorkOrder.work_order_number.desc(),
        )
        .limit(limit)
        .offset(offset)
    ).all()

    result = [
        (
            row[0],
            row[1],
            row[2],
            row[3],
        )
        for row in rows
    ]

    return result, int(total or 0)
