from typing import Annotated

from fastapi import APIRouter, Path

from app.api.deps import DbSession, StaffUser
from app.schemas.history import (
    ClientHistoryResponse,
    VehicleHistoryResponse,
)
from app.services.history import (
    get_client_history,
    get_vehicle_history,
)

router = APIRouter(
    tags=["history"],
)


@router.get(
    "/clients/{client_number}/history",
    response_model=ClientHistoryResponse,
    summary="Полная история клиента",
)
def client_history(
    client_number: Annotated[
        int,
        Path(
            ge=1,
            description="Номер клиента",
        ),
    ],
    db: DbSession,
    _current_user: StaffUser,
) -> ClientHistoryResponse:
    return get_client_history(
        db,
        client_number,
    )


@router.get(
    "/vehicles/{vehicle_number}/history",
    response_model=VehicleHistoryResponse,
    summary="Полная история автомобиля",
)
def vehicle_history(
    vehicle_number: Annotated[
        int,
        Path(
            ge=1,
            description="Номер автомобиля",
        ),
    ],
    db: DbSession,
    _current_user: StaffUser,
) -> VehicleHistoryResponse:
    return get_vehicle_history(
        db,
        vehicle_number,
    )
