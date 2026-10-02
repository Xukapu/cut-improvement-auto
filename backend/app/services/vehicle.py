from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client_vehicle import ClientVehicle
from app.models.vehicle import Vehicle
from app.repositories.client import get_client_by_number
from app.repositories.vehicle import (
    get_current_ownership,
    get_vehicle_by_number,
    get_vehicle_by_vin,
    list_vehicle_owners,
)
from app.schemas.vehicle import (
    TransferVehicleRequest,
    VehicleCreate,
    VehicleOwnerHistoryItem,
    VehicleOwnerHistoryResponse,
    VehicleResponse,
    VehicleUpdate,
)


def build_vehicle_response(
    vehicle: Vehicle,
    owner_client_number: int,
    owner_name: str,
) -> VehicleResponse:
    return VehicleResponse(
        id=vehicle.id,
        vehicle_number=vehicle.vehicle_number,
        license_plate=vehicle.license_plate,
        vin=vehicle.vin,
        brand=vehicle.brand,
        model=vehicle.model,
        year=vehicle.year,
        mileage=vehicle.mileage,
        current_owner_client_number=owner_client_number,
        current_owner_name=owner_name,
    )


def get_vehicle_response(
    db: Session,
    vehicle: Vehicle,
) -> VehicleResponse:
    current = get_current_ownership(
        db,
        vehicle.id,
    )

    if current is None:
        raise RuntimeError("У автомобиля отсутствует текущий владелец.")

    _ownership, owner = current

    return build_vehicle_response(
        vehicle,
        owner.client_number,
        owner.full_name,
    )


def create_vehicle(
    db: Session,
    payload: VehicleCreate,
) -> VehicleResponse:
    owner = get_client_by_number(
        db,
        payload.owner_client_number,
    )

    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Активный владелец автомобиля не найден.",
        )

    if payload.vin is not None:
        existing = get_vehicle_by_vin(
            db,
            payload.vin,
        )

        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Автомобиль с таким VIN уже существует.",
            )

    vehicle = Vehicle(
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
    db.commit()
    db.refresh(vehicle)

    return build_vehicle_response(
        vehicle,
        owner.client_number,
        owner.full_name,
    )


def update_vehicle(
    db: Session,
    *,
    vehicle: Vehicle,
    payload: VehicleUpdate,
) -> VehicleResponse:
    if payload.vin is not None:
        existing = get_vehicle_by_vin(
            db,
            payload.vin,
        )

        if existing is not None and existing.id != vehicle.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Автомобиль с таким VIN уже существует.",
            )

    for field, value in payload.model_dump().items():
        setattr(vehicle, field, value)

    db.commit()
    db.refresh(vehicle)

    return get_vehicle_response(
        db,
        vehicle,
    )


def transfer_vehicle(
    db: Session,
    *,
    vehicle: Vehicle,
    payload: TransferVehicleRequest,
) -> VehicleResponse:
    new_owner = get_client_by_number(
        db,
        payload.new_owner_client_number,
    )

    if new_owner is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Новый активный владелец не найден.",
        )

    current = get_current_ownership(
        db,
        vehicle.id,
    )

    if current is None:
        raise RuntimeError("У автомобиля отсутствует текущий владелец.")

    current_ownership, current_owner = current

    if current_owner.id == new_owner.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Этот клиент уже является владельцем автомобиля.",
        )

    today = date.today()

    current_ownership.is_current = False
    current_ownership.ended_at = today

    new_ownership = ClientVehicle(
        client_id=new_owner.id,
        vehicle_id=vehicle.id,
        is_current=True,
        started_at=today,
    )

    db.add(new_ownership)
    db.commit()
    db.refresh(vehicle)

    return build_vehicle_response(
        vehicle,
        new_owner.client_number,
        new_owner.full_name,
    )


def get_vehicle_owner_history(
    db: Session,
    vehicle: Vehicle,
) -> VehicleOwnerHistoryResponse:
    rows = list_vehicle_owners(
        db,
        vehicle.id,
    )

    return VehicleOwnerHistoryResponse(
        vehicle_number=vehicle.vehicle_number,
        owners=[
            VehicleOwnerHistoryItem(
                client_number=owner.client_number,
                client_name=owner.full_name,
                is_current=ownership.is_current,
                started_at=ownership.started_at,
                ended_at=ownership.ended_at,
            )
            for ownership, owner in rows
        ],
    )


def require_vehicle(
    db: Session,
    vehicle_number: int,
) -> Vehicle:
    vehicle = get_vehicle_by_number(
        db,
        vehicle_number,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автомобиль не найден.",
        )

    return vehicle
