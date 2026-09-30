from typing import Annotated

from fastapi import APIRouter, Path, status

from app.api.deps import DbSession, ManagerUser, StaffUser
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentSummaryResponse,
    PaymentUpdate,
)
from app.services.payment import (
    create_payment,
    delete_payment,
    get_payment_summary,
    update_payment,
)

_SUMMARY_PAYMENT = (
    "\u0423\u0447\u0451\u0442 "
    "\u043e\u043f\u043b\u0430\u0442\u044b "
    "\u0438 "
    "\u0437\u0430\u0434\u043e\u043b\u0436\u0435\u043d\u043d\u043e\u0441\u0442\u0438"
)

_SUMMARY_ADD_PAYMENT = (
    "\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043e\u043f\u043b\u0430\u0442\u0443"
)

_SUMMARY_EDIT_PAYMENT = (
    "\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c \u043e\u043f\u043b\u0430\u0442\u0443"
)

_SUMMARY_DELETE_PAYMENT = (
    "\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u043e\u043f\u043b\u0430\u0442\u0443"
)


router = APIRouter(
    prefix="/work-orders",
    tags=["payments"],
)

PositiveNumber = Annotated[
    int,
    Path(ge=1),
]


@router.get(
    "/{work_order_number}/payment",
    response_model=PaymentSummaryResponse,
    summary=_SUMMARY_PAYMENT,
)
def payment_summary(
    work_order_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> PaymentSummaryResponse:
    return get_payment_summary(
        db,
        work_order_number,
    )


@router.post(
    "/{work_order_number}/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary=_SUMMARY_ADD_PAYMENT,
)
def add_payment(
    work_order_number: PositiveNumber,
    payload: PaymentCreate,
    db: DbSession,
    _current_user: ManagerUser,
) -> PaymentResponse:
    return create_payment(
        db,
        work_order_number=work_order_number,
        payload=payload,
    )


@router.put(
    "/{work_order_number}/payments/{payment_number}",
    response_model=PaymentResponse,
    summary=_SUMMARY_EDIT_PAYMENT,
)
def edit_payment(
    work_order_number: PositiveNumber,
    payment_number: PositiveNumber,
    payload: PaymentUpdate,
    db: DbSession,
    _current_user: ManagerUser,
) -> PaymentResponse:
    return update_payment(
        db,
        work_order_number=work_order_number,
        payment_number=payment_number,
        payload=payload,
    )


@router.delete(
    "/{work_order_number}/payments/{payment_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=_SUMMARY_DELETE_PAYMENT,
)
def remove_payment(
    work_order_number: PositiveNumber,
    payment_number: PositiveNumber,
    db: DbSession,
    _current_user: ManagerUser,
) -> None:
    delete_payment(
        db,
        work_order_number=work_order_number,
        payment_number=payment_number,
    )
