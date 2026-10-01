from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import (
    DbSession,
    OwnerOnly,
    StaffUser,
)
from app.schemas.report import (
    ClientReportResponse,
    EmployeeAccrualReportResponse,
    FinanceReportResponse,
    WorkReportResponse,
)
from app.services.report import (
    get_client_report,
    get_employee_accrual_report,
    get_finance_report,
    get_work_report,
)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)


OptionalDate = Annotated[
    date | None,
    Query(),
]


@router.get(
    "/clients",
    response_model=ClientReportResponse,
    summary="Отчёт по клиентам",
)
def client_report(
    db: DbSession,
    _current_user: StaffUser,
    date_from: OptionalDate = None,
    date_to: OptionalDate = None,
) -> ClientReportResponse:
    return get_client_report(
        db,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/finance",
    response_model=FinanceReportResponse,
    summary="Финансовый отчёт",
)
def finance_report(
    db: DbSession,
    _current_user: OwnerOnly,
    date_from: OptionalDate = None,
    date_to: OptionalDate = None,
) -> FinanceReportResponse:
    return get_finance_report(
        db,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/works",
    response_model=WorkReportResponse,
    summary="Отчёт по выполненным работам",
)
def works_report(
    db: DbSession,
    _current_user: StaffUser,
    date_from: OptionalDate = None,
    date_to: OptionalDate = None,
) -> WorkReportResponse:
    return get_work_report(
        db,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/employee-accruals",
    response_model=EmployeeAccrualReportResponse,
    summary="Начисления сотрудникам",
)
def employee_accrual_report(
    db: DbSession,
    _current_user: OwnerOnly,
    date_from: OptionalDate = None,
    date_to: OptionalDate = None,
) -> EmployeeAccrualReportResponse:
    return get_employee_accrual_report(
        db,
        date_from=date_from,
        date_to=date_to,
    )
