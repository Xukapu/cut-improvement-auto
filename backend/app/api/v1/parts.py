from typing import Annotated

from fastapi import APIRouter, Path, status

from app.api.deps import DbSession, OwnerOrTechAdmin, StaffUser
from app.schemas.part import (
    PartCreate,
    PartListResponse,
    PartResponse,
    PartUpdate,
)
from app.services.part import (
    create_part,
    delete_part,
    get_order_parts,
    update_part,
)

router = APIRouter(
    prefix="/work-orders",
    tags=["parts"],
)

PositiveNumber = Annotated[
    int,
    Path(ge=1),
]


@router.get(
    "/{work_order_number}/parts",
    response_model=PartListResponse,
    summary="Запчасти заказ-наряда",
)
def get_parts(
    work_order_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> PartListResponse:
    return get_order_parts(
        db,
        work_order_number,
    )


@router.post(
    "/{work_order_number}/parts",
    response_model=PartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить запчасть",
)
def add_part(
    work_order_number: PositiveNumber,
    payload: PartCreate,
    db: DbSession,
    _current_user: OwnerOrTechAdmin,
) -> PartResponse:
    return create_part(
        db,
        work_order_number=work_order_number,
        payload=payload,
    )


@router.put(
    "/{work_order_number}/parts/{part_number}",
    response_model=PartResponse,
    summary="Изменить запчасть",
)
def edit_part(
    work_order_number: PositiveNumber,
    part_number: PositiveNumber,
    payload: PartUpdate,
    db: DbSession,
    _current_user: OwnerOrTechAdmin,
) -> PartResponse:
    return update_part(
        db,
        work_order_number=work_order_number,
        part_number=part_number,
        payload=payload,
    )


@router.delete(
    "/{work_order_number}/parts/{part_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить запчасть",
)
def remove_part(
    work_order_number: PositiveNumber,
    part_number: PositiveNumber,
    db: DbSession,
    _current_user: OwnerOrTechAdmin,
) -> None:
    delete_part(
        db,
        work_order_number=work_order_number,
        part_number=part_number,
    )
