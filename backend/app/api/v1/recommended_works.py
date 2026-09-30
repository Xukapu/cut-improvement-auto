from typing import Annotated

from fastapi import APIRouter, Path, status

from app.api.deps import DbSession, StaffUser
from app.schemas.recommended_work import (
    RecommendedWorkCreate,
    RecommendedWorkListResponse,
    RecommendedWorkResponse,
    RecommendedWorkUpdate,
)
from app.services.recommended_work import (
    create_recommended_work,
    delete_recommended_work,
    get_order_recommended_works,
    update_recommended_work,
)

router = APIRouter(
    prefix="/work-orders",
    tags=["recommended-works"],
)

PositiveNumber = Annotated[
    int,
    Path(ge=1),
]


@router.get(
    "/{work_order_number}/recommended-works",
    response_model=RecommendedWorkListResponse,
    summary="Рекомендованные работы заказ-наряда",
)
def get_recommended_works(
    work_order_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> RecommendedWorkListResponse:
    return get_order_recommended_works(
        db,
        work_order_number,
    )


@router.post(
    "/{work_order_number}/recommended-works",
    response_model=RecommendedWorkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить рекомендованную работу",
)
def add_recommended_work(
    work_order_number: PositiveNumber,
    payload: RecommendedWorkCreate,
    db: DbSession,
    _current_user: StaffUser,
) -> RecommendedWorkResponse:
    return create_recommended_work(
        db,
        work_order_number=work_order_number,
        payload=payload,
    )


@router.put(
    ("/{work_order_number}/recommended-works/{recommended_work_number}"),
    response_model=RecommendedWorkResponse,
    summary="Изменить рекомендованную работу",
)
def edit_recommended_work(
    work_order_number: PositiveNumber,
    recommended_work_number: PositiveNumber,
    payload: RecommendedWorkUpdate,
    db: DbSession,
    _current_user: StaffUser,
) -> RecommendedWorkResponse:
    return update_recommended_work(
        db,
        work_order_number=work_order_number,
        recommended_work_number=recommended_work_number,
        payload=payload,
    )


@router.delete(
    ("/{work_order_number}/recommended-works/{recommended_work_number}"),
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить рекомендованную работу",
)
def remove_recommended_work(
    work_order_number: PositiveNumber,
    recommended_work_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> None:
    delete_recommended_work(
        db,
        work_order_number=work_order_number,
        recommended_work_number=recommended_work_number,
    )
