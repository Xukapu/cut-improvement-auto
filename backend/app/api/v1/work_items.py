from typing import Annotated

from fastapi import APIRouter, Path, status

from app.api.deps import DbSession, OwnerOnly, StaffUser
from app.schemas.work_item import (
    WorkItemCreate,
    WorkItemFinancialListResponse,
    WorkItemFinancialResponse,
    WorkItemListResponse,
    WorkItemUpdate,
)
from app.services.work_item import (
    create_work_item,
    get_order_work_items,
    get_order_work_items_financial,
    update_work_item,
)

router = APIRouter(
    prefix="/work-orders",
    tags=["work-items"],
)

PositiveNumber = Annotated[
    int,
    Path(ge=1),
]


@router.get(
    "/{work_order_number}/works",
    response_model=WorkItemListResponse,
    summary="Работы заказ-наряда",
)
def get_works(
    work_order_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> WorkItemListResponse:
    items = get_order_work_items(
        db,
        work_order_number,
    )

    return WorkItemListResponse(
        items=items,
        total=len(items),
    )


@router.get(
    "/{work_order_number}/works/financial",
    response_model=WorkItemFinancialListResponse,
    summary="Расчёт работ и начислений — только владелец",
)
def get_works_financial(
    work_order_number: PositiveNumber,
    db: DbSession,
    _current_user: OwnerOnly,
) -> WorkItemFinancialListResponse:
    items = get_order_work_items_financial(
        db,
        work_order_number,
    )

    return WorkItemFinancialListResponse(
        items=items,
        total=len(items),
    )


@router.post(
    "/{work_order_number}/works",
    response_model=WorkItemFinancialResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить работу — только владелец",
)
def add_work(
    work_order_number: PositiveNumber,
    payload: WorkItemCreate,
    db: DbSession,
    _current_user: OwnerOnly,
) -> WorkItemFinancialResponse:
    return create_work_item(
        db,
        work_order_number=work_order_number,
        payload=payload,
    )


@router.put(
    "/{work_order_number}/works/{work_item_number}",
    response_model=WorkItemFinancialResponse,
    summary="Изменить работу и исполнителей — только владелец",
)
def edit_work(
    work_order_number: PositiveNumber,
    work_item_number: PositiveNumber,
    payload: WorkItemUpdate,
    db: DbSession,
    _current_user: OwnerOnly,
) -> WorkItemFinancialResponse:
    return update_work_item(
        db,
        work_order_number=work_order_number,
        work_item_number=work_item_number,
        payload=payload,
    )
