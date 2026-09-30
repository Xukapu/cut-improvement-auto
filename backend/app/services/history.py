from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.history import (
    get_client_appointment_history,
    get_client_for_history,
    get_client_vehicle_history,
    get_vehicle_appointment_history,
    get_vehicle_for_history,
    get_vehicle_owner_history,
)
from app.schemas.history import (
    ClientHistoryAppointment,
    ClientHistoryResponse,
    ClientHistoryVehicle,
    VehicleHistoryAppointment,
    VehicleHistoryOwner,
    VehicleHistoryResponse,
)


def get_client_history(
    db: Session,
    client_number: int,
) -> ClientHistoryResponse:
    client = get_client_for_history(
        db,
        client_number,
    )

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден.",
        )

    vehicle_rows = get_client_vehicle_history(
        db,
        client.id,
    )

    appointment_rows = get_client_appointment_history(
        db,
        client.id,
    )

    return ClientHistoryResponse(
        client_number=client.client_number,
        full_name=client.full_name,
        phone_primary=client.phone_primary,
        phone_secondary=client.phone_secondary,
        source=client.source,
        referred_by_client_number=client.referred_by_client_number,
        referred_by_client_name=client.referred_by_client_name,
        internal_mark=client.internal_mark,
        notes=client.notes,
        is_archived=client.archived_at is not None,
        vehicles=[
            ClientHistoryVehicle(
                vehicle_number=vehicle.vehicle_number,
                license_plate=vehicle.license_plate,
                vin=vehicle.vin,
                brand=vehicle.brand,
                model=vehicle.model,
                year=vehicle.year,
                mileage=vehicle.mileage,
                is_current_owner=ownership.is_current,
                ownership_started_at=ownership.started_at,
                ownership_ended_at=ownership.ended_at,
            )
            for ownership, vehicle in vehicle_rows
        ],
        appointments=[
            ClientHistoryAppointment(
                appointment_number=appointment.appointment_number,
                vehicle_number=vehicle.vehicle_number,
                license_plate=vehicle.license_plate,
                appointment_date=appointment.appointment_date,
                appointment_time=appointment.appointment_time,
                reason=appointment.reason,
                comment=appointment.comment,
                status=appointment.status,
            )
            for appointment, vehicle in appointment_rows
        ],
    )


def get_vehicle_history(
    db: Session,
    vehicle_number: int,
) -> VehicleHistoryResponse:
    vehicle = get_vehicle_for_history(
        db,
        vehicle_number,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автомобиль не найден.",
        )

    owner_rows = get_vehicle_owner_history(
        db,
        vehicle.id,
    )

    appointment_rows = get_vehicle_appointment_history(
        db,
        vehicle.id,
    )

    return VehicleHistoryResponse(
        vehicle_number=vehicle.vehicle_number,
        license_plate=vehicle.license_plate,
        vin=vehicle.vin,
        brand=vehicle.brand,
        model=vehicle.model,
        year=vehicle.year,
        mileage=vehicle.mileage,
        owners=[
            VehicleHistoryOwner(
                client_number=client.client_number,
                client_name=client.full_name,
                is_current=ownership.is_current,
                started_at=ownership.started_at,
                ended_at=ownership.ended_at,
            )
            for ownership, client in owner_rows
        ],
        appointments=[
            VehicleHistoryAppointment(
                appointment_number=appointment.appointment_number,
                client_number=client.client_number,
                client_name=client.full_name,
                appointment_date=appointment.appointment_date,
                appointment_time=appointment.appointment_time,
                reason=appointment.reason,
                comment=appointment.comment,
                status=appointment.status,
            )
            for appointment, client in appointment_rows
        ],
    )
