from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.work_item import WorkItem, WorkItemAssignment
from app.models.work_order import WorkOrderStatus
from app.repositories.employee import (
    get_current_employee_rate,
    get_employee_by_number,
)
from app.repositories.work_item import (
    get_work_item_by_number,
    list_assignments_for_work,
    list_work_items_for_order,
)
from app.schemas.work_item import (
    WorkAssignmentFinancialResponse,
    WorkAssignmentPublicResponse,
    WorkItemFinancialResponse,
    WorkItemPublicResponse,
    WorkItemWrite,
)
from app.services.work_order import require_work_order

_MONEY = Decimal("0.01")


def calculate_earning(
    *,
    price: Decimal,
    share_percent: Decimal,
    rate_percent: Decimal,
) -> Decimal:
    amount = price * share_percent / Decimal("100") * rate_percent / Decimal("100")

    return amount.quantize(
        _MONEY,
        rounding=ROUND_HALF_UP,
    )


def ensure_order_editable(order) -> None:
    if order.status == WorkOrderStatus.ISSUED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Нельзя изменять работы в выданном заказ-наряде."),
        )


def build_public_work_item_response(
    db: Session,
    work_item: WorkItem,
) -> WorkItemPublicResponse:
    assignments = list_assignments_for_work(
        db,
        work_item.id,
    )

    return WorkItemPublicResponse(
        work_item_number=work_item.work_item_number,
        name=work_item.name,
        price=work_item.price,
        assignments=[
            WorkAssignmentPublicResponse(
                employee_number=employee.employee_number,
                employee_name=employee.full_name,
            )
            for _assignment, employee in assignments
        ],
    )


def build_financial_work_item_response(
    db: Session,
    work_item: WorkItem,
) -> WorkItemFinancialResponse:
    assignments = list_assignments_for_work(
        db,
        work_item.id,
    )

    response_assignments = []
    total_earnings = Decimal("0")

    for assignment, employee in assignments:
        earning = calculate_earning(
            price=work_item.price,
            share_percent=assignment.share_percent,
            rate_percent=assignment.rate_percent_snapshot,
        )

        total_earnings += earning

        response_assignments.append(
            WorkAssignmentFinancialResponse(
                employee_number=employee.employee_number,
                employee_name=employee.full_name,
                share_percent=assignment.share_percent,
                rate_percent_snapshot=(assignment.rate_percent_snapshot),
                earning_amount=earning,
            )
        )

    return WorkItemFinancialResponse(
        work_item_number=work_item.work_item_number,
        name=work_item.name,
        price=work_item.price,
        assignments=response_assignments,
        total_employee_earnings=total_earnings.quantize(
            _MONEY,
            rounding=ROUND_HALF_UP,
        ),
    )


def add_assignments(
    db: Session,
    *,
    work_item: WorkItem,
    payload: WorkItemWrite,
) -> None:
    for item in payload.assignments:
        employee = get_employee_by_number(
            db,
            item.employee_number,
        )

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(f"Сотрудник №{item.employee_number} не найден."),
            )

        if not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(f"Сотрудник №{item.employee_number} неактивен."),
            )

        rate = get_current_employee_rate(
            db,
            employee.id,
        )

        if rate is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(f"У сотрудника №{item.employee_number} не задана ставка."),
            )

        assignment = WorkItemAssignment(
            work_item_id=work_item.id,
            employee_id=employee.id,
            share_percent=item.share_percent,
            rate_percent_snapshot=rate.rate_percent,
        )

        db.add(assignment)


def create_work_item(
    db: Session,
    *,
    work_order_number: int,
    payload: WorkItemWrite,
) -> WorkItemFinancialResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    ensure_order_editable(order)

    work_item = WorkItem(
        work_order_id=order.id,
        name=payload.name,
        price=payload.price,
    )

    db.add(work_item)
    db.flush()

    add_assignments(
        db,
        work_item=work_item,
        payload=payload,
    )

    db.commit()
    db.refresh(work_item)

    return build_financial_work_item_response(
        db,
        work_item,
    )


def update_work_item(
    db: Session,
    *,
    work_order_number: int,
    work_item_number: int,
    payload: WorkItemWrite,
) -> WorkItemFinancialResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    ensure_order_editable(order)

    work_item = get_work_item_by_number(
        db,
        work_item_number,
    )

    if work_item is None or work_item.work_order_id != order.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Работа в этом заказ-наряде не найдена.",
        )

    work_item.name = payload.name
    work_item.price = payload.price

    db.execute(delete(WorkItemAssignment).where(WorkItemAssignment.work_item_id == work_item.id))

    add_assignments(
        db,
        work_item=work_item,
        payload=payload,
    )

    db.commit()
    db.refresh(work_item)

    return build_financial_work_item_response(
        db,
        work_item,
    )


def get_order_work_items(
    db: Session,
    work_order_number: int,
) -> list[WorkItemPublicResponse]:
    order = require_work_order(
        db,
        work_order_number,
    )

    items = list_work_items_for_order(
        db,
        order.id,
    )

    return [
        build_public_work_item_response(
            db,
            item,
        )
        for item in items
    ]


def get_order_work_items_financial(
    db: Session,
    work_order_number: int,
) -> list[WorkItemFinancialResponse]:
    order = require_work_order(
        db,
        work_order_number,
    )

    items = list_work_items_for_order(
        db,
        order.id,
    )

    return [
        build_financial_work_item_response(
            db,
            item,
        )
        for item in items
    ]
