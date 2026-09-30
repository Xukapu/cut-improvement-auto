from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.api.deps import DbSession, ManagerUser, StaffUser
from app.repositories.vehicle import list_vehicles
from app.schemas.vehicle import (
    TransferVehicleRequest,
    VehicleCreate,
    VehicleListResponse,
    VehicleOwnerHistoryResponse,
    VehicleResponse,
    VehicleUpdate,
)
from app.services.vehicle import (
    build_vehicle_response,
    create_vehicle,
    get_vehicle_owner_history,
    get_vehicle_response,
    require_vehicle,
    transfer_vehicle,
    update_vehicle,
)

router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
)

VehicleNumber = Annotated[
    int,
    Path(
        ge=1,
        description="Номер автомобиля",
    ),
]


@router.get(
    "",
    response_model=VehicleListResponse,
    summary="Список и поиск автомобилей",
)
def get_vehicles(
    db: DbSession,
    _current_user: StaffUser,
    search: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=200,
        ),
    ] = None,
    client_number: Annotated[
        int | None,
        Query(
            ge=1,
            description="Текущий владелец",
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
        ),
    ] = 50,
    offset: Annotated[
        int,
        Query(
            ge=0,
        ),
    ] = 0,
) -> VehicleListResponse:
    rows, total = list_vehicles(
        db,
        search=search,
        client_number=client_number,
        limit=limit,
        offset=offset,
    )

    return VehicleListResponse(
        items=[
            build_vehicle_response(
                vehicle,
                owner_number,
                owner_name,
            )
            for vehicle, owner_number, owner_name in rows
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{vehicle_number}",
    response_model=VehicleResponse,
    summary="Карточка автомобиля",
)
def get_vehicle(
    vehicle_number: VehicleNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> VehicleResponse:
    vehicle = require_vehicle(
        db,
        vehicle_number,
    )

    return get_vehicle_response(
        db,
        vehicle,
    )


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать автомобиль",
)
def add_vehicle(
    payload: VehicleCreate,
    db: DbSession,
    _current_user: ManagerUser,
) -> VehicleResponse:
    return create_vehicle(
        db,
        payload,
    )


@router.put(
    "/{vehicle_number}",
    response_model=VehicleResponse,
    summary="Изменить автомобиль",
)
def edit_vehicle(
    vehicle_number: VehicleNumber,
    payload: VehicleUpdate,
    db: DbSession,
    _current_user: ManagerUser,
) -> VehicleResponse:
    vehicle = require_vehicle(
        db,
        vehicle_number,
    )

    return update_vehicle(
        db,
        vehicle=vehicle,
        payload=payload,
    )


@router.post(
    "/{vehicle_number}/transfer",
    response_model=VehicleResponse,
    summary="Сменить владельца автомобиля",
)
def change_vehicle_owner(
    vehicle_number: VehicleNumber,
    payload: TransferVehicleRequest,
    db: DbSession,
    _current_user: ManagerUser,
) -> VehicleResponse:
    vehicle = require_vehicle(
        db,
        vehicle_number,
    )

    return transfer_vehicle(
        db,
        vehicle=vehicle,
        payload=payload,
    )


@router.get(
    "/{vehicle_number}/owners",
    response_model=VehicleOwnerHistoryResponse,
    summary="История владельцев автомобиля",
)
def get_vehicle_owners(
    vehicle_number: VehicleNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> VehicleOwnerHistoryResponse:
    vehicle = require_vehicle(
        db,
        vehicle_number,
    )

    return get_vehicle_owner_history(
        db,
        vehicle,
    )
