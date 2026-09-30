from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.api.deps import (
    DbSession,
    OwnerOrTechAdmin,
    StaffUser,
)
from app.models.work_order import WorkOrderStatus
from app.repositories.work_order import list_work_orders
from app.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderListResponse,
    WorkOrderResponse,
    WorkOrderStatusUpdate,
    WorkOrderUpdate,
)
from app.services.work_order import (
    build_work_order_response,
    change_work_order_status,
    create_work_order,
    get_work_order_response,
    require_work_order,
    update_work_order,
)

router = APIRouter(
    prefix="/work-orders",
    tags=["work-orders"],
)

WorkOrderNumber = Annotated[
    int,
    Path(
        ge=1,
        description="Номер заказ-наряда",
    ),
]


@router.get(
    "",
    response_model=WorkOrderListResponse,
    summary="Список заказ-нарядов",
)
def get_work_orders(
    db: DbSession,
    _current_user: StaffUser,
    order_status: Annotated[
        WorkOrderStatus | None,
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
) -> WorkOrderListResponse:
    rows, total = list_work_orders(
        db,
        status=order_status,
        client_number=client_number,
        vehicle_number=vehicle_number,
        limit=limit,
        offset=offset,
    )

    return WorkOrderListResponse(
        items=[
            build_work_order_response(
                order,
                client=client,
                vehicle=vehicle,
                appointment=appointment,
            )
            for (
                order,
                client,
                vehicle,
                appointment,
            ) in rows
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{work_order_number}",
    response_model=WorkOrderResponse,
    summary="Карточка заказ-наряда",
)
def get_work_order(
    work_order_number: WorkOrderNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> WorkOrderResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    return get_work_order_response(
        db,
        order,
    )


@router.post(
    "",
    response_model=WorkOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заказ-наряд",
)
def add_work_order(
    payload: WorkOrderCreate,
    db: DbSession,
    _current_user: OwnerOrTechAdmin,
) -> WorkOrderResponse:
    return create_work_order(
        db,
        payload,
    )


@router.put(
    "/{work_order_number}",
    response_model=WorkOrderResponse,
    summary="Изменить заказ-наряд",
)
def edit_work_order(
    work_order_number: WorkOrderNumber,
    payload: WorkOrderUpdate,
    db: DbSession,
    _current_user: OwnerOrTechAdmin,
) -> WorkOrderResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    return update_work_order(
        db,
        order=order,
        payload=payload,
    )


@router.patch(
    "/{work_order_number}/status",
    response_model=WorkOrderResponse,
    summary="Изменить статус заказ-наряда",
)
def edit_work_order_status(
    work_order_number: WorkOrderNumber,
    payload: WorkOrderStatusUpdate,
    db: DbSession,
    _current_user: OwnerOrTechAdmin,
) -> WorkOrderResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    return change_work_order_status(
        db,
        order=order,
        new_status=payload.status,
    )
