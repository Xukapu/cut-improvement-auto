from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.repositories.appointment import (
    get_appointment_by_number,
    get_appointment_details,
)
from app.repositories.client import get_client_by_number
from app.repositories.vehicle import (
    get_current_ownership,
    get_vehicle_by_number,
)
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)


def validate_client_vehicle(
    db: Session,
    *,
    client_number: int,
    vehicle_number: int,
) -> tuple:
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

    _ownership_record, current_owner = ownership

    if current_owner.id != client.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("Указанный автомобиль не принадлежит этому клиенту."),
        )

    return client, vehicle


def build_appointment_response(
    appointment: Appointment,
    *,
    client_number: int,
    client_name: str,
    vehicle_number: int,
    license_plate: str,
) -> AppointmentResponse:
    return AppointmentResponse(
        appointment_number=appointment.appointment_number,
        client_number=client_number,
        client_name=client_name,
        vehicle_number=vehicle_number,
        license_plate=license_plate,
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        reason=appointment.reason,
        comment=appointment.comment,
        status=appointment.status,
    )


def get_appointment_response(
    db: Session,
    appointment: Appointment,
) -> AppointmentResponse:
    details = get_appointment_details(
        db,
        appointment.id,
    )

    if details is None:
        raise RuntimeError("Не удалось получить данные записи.")

    _appointment, client, vehicle = details

    return build_appointment_response(
        appointment,
        client_number=client.client_number,
        client_name=client.full_name,
        vehicle_number=vehicle.vehicle_number,
        license_plate=vehicle.license_plate,
    )


def create_appointment(
    db: Session,
    payload: AppointmentCreate,
) -> AppointmentResponse:
    client, vehicle = validate_client_vehicle(
        db,
        client_number=payload.client_number,
        vehicle_number=payload.vehicle_number,
    )

    appointment = Appointment(
        client_id=client.id,
        vehicle_id=vehicle.id,
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
        reason=payload.reason,
        comment=payload.comment,
        status=payload.status,
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return build_appointment_response(
        appointment,
        client_number=client.client_number,
        client_name=client.full_name,
        vehicle_number=vehicle.vehicle_number,
        license_plate=vehicle.license_plate,
    )


def update_appointment(
    db: Session,
    *,
    appointment: Appointment,
    payload: AppointmentUpdate,
) -> AppointmentResponse:
    client, vehicle = validate_client_vehicle(
        db,
        client_number=payload.client_number,
        vehicle_number=payload.vehicle_number,
    )

    appointment.client_id = client.id
    appointment.vehicle_id = vehicle.id

    appointment.appointment_date = payload.appointment_date
    appointment.appointment_time = payload.appointment_time

    appointment.reason = payload.reason
    appointment.comment = payload.comment
    appointment.status = payload.status

    db.commit()
    db.refresh(appointment)

    return build_appointment_response(
        appointment,
        client_number=client.client_number,
        client_name=client.full_name,
        vehicle_number=vehicle.vehicle_number,
        license_plate=vehicle.license_plate,
    )


def require_appointment(
    db: Session,
    appointment_number: int,
) -> Appointment:
    appointment = get_appointment_by_number(
        db,
        appointment_number,
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена.",
        )

    return appointment
