from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.models.client import Client
from app.models.client_vehicle import ClientVehicle
from app.models.vehicle import Vehicle

CurrentOwnership = aliased(ClientVehicle)
CurrentOwner = aliased(Client)


def get_vehicle_by_number(
    db: Session,
    vehicle_number: int,
) -> Vehicle | None:
    return db.scalar(
        select(Vehicle).where(
            Vehicle.vehicle_number == vehicle_number,
            Vehicle.deleted_at.is_(None),
        )
    )


def get_vehicle_by_vin(
    db: Session,
    vin: str,
) -> Vehicle | None:
    return db.scalar(
        select(Vehicle).where(
            Vehicle.vin == vin,
            Vehicle.deleted_at.is_(None),
        )
    )


def get_current_ownership(
    db: Session,
    vehicle_id: UUID,
) -> tuple[ClientVehicle, Client] | None:
    row = db.execute(
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
            ClientVehicle.is_current.is_(True),
            ClientVehicle.deleted_at.is_(None),
        )
    ).first()

    if row is None:
        return None

    return row[0], row[1]


def list_vehicle_owners(
    db: Session,
    vehicle_id: UUID,
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
        )
        .order_by(
            ClientVehicle.started_at.desc(),
            ClientVehicle.created_at.desc(),
        )
    ).all()

    return [(row[0], row[1]) for row in rows]


def list_vehicles(
    db: Session,
    *,
    search: str | None,
    client_number: int | None,
    limit: int,
    offset: int,
) -> tuple[list[tuple[Vehicle, int, str]], int]:
    filters = [
        Vehicle.deleted_at.is_(None),
        CurrentOwnership.is_current.is_(True),
        CurrentOwnership.deleted_at.is_(None),
    ]

    if client_number is not None:
        filters.append(CurrentOwner.client_number == client_number)

    if search:
        value = search.strip()

        if value:
            pattern = f"%{value}%"

            search_conditions = [
                Vehicle.license_plate.ilike(pattern),
                Vehicle.vin.ilike(pattern),
                Vehicle.brand.ilike(pattern),
                Vehicle.model.ilike(pattern),
                (Vehicle.brand + " " + Vehicle.model).ilike(pattern),
            ]

            if value.isdigit():
                search_conditions.append(Vehicle.vehicle_number == int(value))

            filters.append(or_(*search_conditions))

    base_query = (
        select(
            Vehicle,
            CurrentOwner.client_number,
            CurrentOwner.full_name,
        )
        .join(
            CurrentOwnership,
            and_(
                CurrentOwnership.vehicle_id == Vehicle.id,
                CurrentOwnership.is_current.is_(True),
                CurrentOwnership.deleted_at.is_(None),
            ),
        )
        .join(
            CurrentOwner,
            CurrentOwner.id == CurrentOwnership.client_id,
        )
        .where(*filters)
    )

    total = db.scalar(select(func.count()).select_from(base_query.subquery()))

    rows = db.execute(
        base_query.order_by(Vehicle.vehicle_number.asc()).limit(limit).offset(offset)
    ).all()

    result = [
        (
            row[0],
            int(row[1]),
            str(row[2]),
        )
        for row in rows
    ]

    return result, int(total or 0)
