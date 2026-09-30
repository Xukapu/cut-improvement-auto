from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.client import Client
from app.models.client_vehicle import ClientVehicle
from app.models.vehicle import Vehicle


def get_client_for_history(
    db: Session,
    client_number: int,
) -> Client | None:
    return db.scalar(
        select(Client).where(
            Client.client_number == client_number,
            Client.deleted_at.is_(None),
        )
    )


def get_vehicle_for_history(
    db: Session,
    vehicle_number: int,
) -> Vehicle | None:
    return db.scalar(
        select(Vehicle).where(
            Vehicle.vehicle_number == vehicle_number,
            Vehicle.deleted_at.is_(None),
        )
    )


def get_client_vehicle_history(
    db: Session,
    client_id,
) -> list[tuple[ClientVehicle, Vehicle]]:
    rows = db.execute(
        select(
            ClientVehicle,
            Vehicle,
        )
        .join(
            Vehicle,
            Vehicle.id == ClientVehicle.vehicle_id,
        )
        .where(
            ClientVehicle.client_id == client_id,
            ClientVehicle.deleted_at.is_(None),
            Vehicle.deleted_at.is_(None),
        )
        .order_by(
            ClientVehicle.is_current.desc(),
            ClientVehicle.started_at.desc(),
            Vehicle.vehicle_number.asc(),
        )
    ).all()

    return [(row[0], row[1]) for row in rows]


def get_client_appointment_history(
    db: Session,
    client_id,
) -> list[tuple[Appointment, Vehicle]]:
    rows = db.execute(
        select(
            Appointment,
            Vehicle,
        )
        .join(
            Vehicle,
            Vehicle.id == Appointment.vehicle_id,
        )
        .where(
            Appointment.client_id == client_id,
            Appointment.deleted_at.is_(None),
            Vehicle.deleted_at.is_(None),
        )
        .order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc(),
            Appointment.appointment_number.desc(),
        )
    ).all()

    return [(row[0], row[1]) for row in rows]


def get_vehicle_owner_history(
    db: Session,
    vehicle_id,
) -> list[tuple[ClientVehicle, Client]]:
    rows = db.execute(
        select(
            ClientVehicle,
            Client,
        )
        .join(
            Client,
            Client.id == ClientVehicle.client_id,
        )
        .where(
            ClientVehicle.vehicle_id == vehicle_id,
            ClientVehicle.deleted_at.is_(None),
            Client.deleted_at.is_(None),
        )
        .order_by(
            ClientVehicle.is_current.desc(),
            ClientVehicle.started_at.desc(),
            Client.client_number.asc(),
        )
    ).all()

    return [(row[0], row[1]) for row in rows]


def get_vehicle_appointment_history(
    db: Session,
    vehicle_id,
) -> list[tuple[Appointment, Client]]:
    rows = db.execute(
        select(
            Appointment,
            Client,
        )
        .join(
            Client,
            Client.id == Appointment.client_id,
        )
        .where(
            Appointment.vehicle_id == vehicle_id,
            Appointment.deleted_at.is_(None),
            Client.deleted_at.is_(None),
        )
        .order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc(),
            Appointment.appointment_number.desc(),
        )
    ).all()

    return [(row[0], row[1]) for row in rows]
