from datetime import date
from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.api.deps import (
    DbSession,
    OwnerOrTechAdmin,
    StaffUser,
)
from app.models.appointment import AppointmentStatus
from app.repositories.appointment import list_appointments
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentListResponse,
    AppointmentResponse,
    AppointmentUpdate,
)
from app.services.appointment import (
    build_appointment_response,
    create_appointment,
    get_appointment_response,
    require_appointment,
    update_appointment,
)

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)

AppointmentNumber = Annotated[
    int,
    Path(
        ge=1,
        description="Номер записи",
    ),
]


@router.get(
    "",
    response_model=AppointmentListResponse,
    summary="Список записей",
)
def get_appointments(
    db: DbSession,
    _current_user: StaffUser,
    appointment_date: date | None = None,
    appointment_status: Annotated[
        AppointmentStatus | None,
        Query(alias="status"),
    ] = None,
    client_number: Annotated[
        int | None,
        Query(ge=1),
    ] = None,
    vehicle_number: Annotated[
        int | None,
        Query(ge=1),
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 50,
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
) -> AppointmentListResponse:
    rows, total = list_appointments(
        db,
        appointment_date=appointment_date,
        status=appointment_status,
        client_number=client_number,
        vehicle_number=vehicle_number,
        limit=limit,
        offset=offset,
    )

    return AppointmentListResponse(
        items=[
            build_appointment_response(
                appointment,
                client_number=client_number_value,
                client_name=client_name,
                vehicle_number=vehicle_number_value,
                license_plate=license_plate,
            )
            for (
                appointment,
                client_number_value,
                client_name,
                vehicle_number_value,
                license_plate,
            ) in rows
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{appointment_number}",
    response_model=AppointmentResponse,
    summary="Карточка записи",
)
def get_appointment(
    appointment_number: AppointmentNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> AppointmentResponse:
    appointment = require_appointment(
        db,
        appointment_number,
    )

    return get_appointment_response(
        db,
        appointment,
    )


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать запись",
)
def add_appointment(
    payload: AppointmentCreate,
    db: DbSession,
    _current_user: OwnerOrTechAdmin,
) -> AppointmentResponse:
    return create_appointment(
        db,
        payload,
    )


@router.put(
    "/{appointment_number}",
    response_model=AppointmentResponse,
    summary="Изменить запись",
)
def edit_appointment(
    appointment_number: AppointmentNumber,
    payload: AppointmentUpdate,
    db: DbSession,
    _current_user: OwnerOrTechAdmin,
) -> AppointmentResponse:
    appointment = require_appointment(
        db,
        appointment_number,
    )

    return update_appointment(
        db,
        appointment=appointment,
        payload=payload,
    )
