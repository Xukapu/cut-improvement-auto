from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.part import Part
from app.models.work_order import WorkOrderStatus
from app.repositories.part import (
    get_part_by_number,
    list_parts_for_order,
)
from app.schemas.part import (
    PartListResponse,
    PartResponse,
    PartWrite,
)
from app.services.work_order import require_work_order

_MONEY = Decimal("0.01")


def ensure_order_parts_editable(order) -> None:
    if order.status == WorkOrderStatus.ISSUED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Нельзя изменять запчасти в выданном заказ-наряде."),
        )


def require_order_part(
    db: Session,
    *,
    order,
    part_number: int,
) -> Part:
    part = get_part_by_number(
        db,
        part_number,
    )

    if part is None or part.work_order_id != order.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запчасть в этом заказ-наряде не найдена.",
        )

    return part


def create_part(
    db: Session,
    *,
    work_order_number: int,
    payload: PartWrite,
) -> PartResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    ensure_order_parts_editable(order)

    part = Part(
        work_order_id=order.id,
        name=payload.name,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        supplier=payload.supplier,
        provided_by=payload.provided_by,
    )

    db.add(part)
    db.commit()
    db.refresh(part)

    return PartResponse.from_part(part)


def update_part(
    db: Session,
    *,
    work_order_number: int,
    part_number: int,
    payload: PartWrite,
) -> PartResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    ensure_order_parts_editable(order)

    part = require_order_part(
        db,
        order=order,
        part_number=part_number,
    )

    part.name = payload.name
    part.quantity = payload.quantity
    part.unit_price = payload.unit_price
    part.supplier = payload.supplier
    part.provided_by = payload.provided_by

    db.commit()
    db.refresh(part)

    return PartResponse.from_part(part)


def delete_part(
    db: Session,
    *,
    work_order_number: int,
    part_number: int,
) -> None:
    order = require_work_order(
        db,
        work_order_number,
    )

    ensure_order_parts_editable(order)

    part = require_order_part(
        db,
        order=order,
        part_number=part_number,
    )

    part.deleted_at = datetime.now(UTC)

    db.commit()


def get_order_parts(
    db: Session,
    work_order_number: int,
) -> PartListResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    parts = list_parts_for_order(
        db,
        order.id,
    )

    responses = [PartResponse.from_part(part) for part in parts]

    total_price = sum(
        (item.total_price for item in responses),
        Decimal("0"),
    ).quantize(
        _MONEY,
        rounding=ROUND_HALF_UP,
    )

    return PartListResponse(
        items=responses,
        total=len(responses),
        total_price=total_price,
    )
