from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.client import list_clients
from app.repositories.vehicle import list_vehicles
from app.schemas.search import (
    GlobalSearchResponse,
    SearchClientResult,
    SearchVehicleResult,
)


def global_search(
    db: Session,
    *,
    query: str,
    limit: int,
) -> GlobalSearchResponse:
    value = query.strip()

    if not value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Введите текст для поиска.",
        )

    clients, total_clients = list_clients(
        db,
        search=value,
        limit=limit,
        offset=0,
    )

    vehicles, total_vehicles = list_vehicles(
        db,
        search=value,
        client_number=None,
        limit=limit,
        offset=0,
    )

    return GlobalSearchResponse(
        query=value,
        clients=[
            SearchClientResult(
                client_number=client.client_number,
                full_name=client.full_name,
                phone_primary=client.phone_primary,
                phone_secondary=client.phone_secondary,
                source=client.source,
                internal_mark=client.internal_mark,
            )
            for client in clients
        ],
        vehicles=[
            SearchVehicleResult(
                vehicle_number=vehicle.vehicle_number,
                license_plate=vehicle.license_plate,
                vin=vehicle.vin,
                brand=vehicle.brand,
                model=vehicle.model,
                year=vehicle.year,
                mileage=vehicle.mileage,
                current_owner_client_number=owner_number,
                current_owner_name=owner_name,
            )
            for vehicle, owner_number, owner_name in vehicles
        ],
        total_clients=total_clients,
        total_vehicles=total_vehicles,
        total=total_clients + total_vehicles,
    )
