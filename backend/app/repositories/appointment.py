from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus
from app.models.client import Client
from app.models.vehicle import Vehicle


def get_appointment_by_number(
    db: Session,
    appointment_number: int,
) -> Appointment | None:
    return db.scalar(
        select(Appointment).where(
            Appointment.appointment_number == appointment_number,
            Appointment.deleted_at.is_(None),
        )
    )


def list_appointments(
    db: Session,
    *,
    appointment_date: date | None,
    status: AppointmentStatus | None,
    client_number: int | None,
    vehicle_number: int | None,
    limit: int,
    offset: int,
) -> tuple[
    list[tuple[Appointment, int, str, int, str]],
    int,
]:
    filters = [
        Appointment.deleted_at.is_(None),
    ]

    if appointment_date is not None:
        filters.append(Appointment.appointment_date == appointment_date)

    if status is not None:
        filters.append(Appointment.status == status)

    if client_number is not None:
        filters.append(Client.client_number == client_number)

    if vehicle_number is not None:
        filters.append(Vehicle.vehicle_number == vehicle_number)

    query = (
        select(
            Appointment,
            Client.client_number,
            Client.full_name,
            Vehicle.vehicle_number,
            Vehicle.license_plate,
        )
        .join(
            Client,
            Client.id == Appointment.client_id,
        )
        .join(
            Vehicle,
            Vehicle.id == Appointment.vehicle_id,
        )
        .where(*filters)
    )

    total = db.scalar(select(func.count()).select_from(query.subquery()))

    rows = db.execute(
        query.order_by(
            Appointment.appointment_date.asc(),
            Appointment.appointment_time.asc(),
            Appointment.appointment_number.asc(),
        )
        .limit(limit)
        .offset(offset)
    ).all()

    result = [
        (
            row[0],
            int(row[1]),
            str(row[2]),
            int(row[3]),
            str(row[4]),
        )
        for row in rows
    ]

    return result, int(total or 0)


def get_appointment_details(
    db: Session,
    appointment_id: UUID,
) -> tuple[Appointment, Client, Vehicle] | None:
    row = db.execute(
        select(
            Appointment,
            Client,
            Vehicle,
        )
        .join(
            Client,
            Client.id == Appointment.client_id,
        )
        .join(
            Vehicle,
            Vehicle.id == Appointment.vehicle_id,
        )
        .where(
            Appointment.id == appointment_id,
            Appointment.deleted_at.is_(None),
        )
    ).first()

    if row is None:
        return None

    return row[0], row[1], row[2]
