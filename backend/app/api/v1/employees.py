from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.api.deps import DbSession, OwnerOnly, StaffUser
from app.repositories.employee import list_employees
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeFinancialResponse,
    EmployeePublicResponse,
    EmployeeRateHistoryResponse,
    EmployeeRateUpdate,
    EmployeeUpdate,
)
from app.services.employee import (
    change_employee_rate,
    create_employee,
    employee_financial_response,
    employee_public_response,
    employee_rate_history,
    require_employee,
    update_employee,
)

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
)

EmployeeNumber = Annotated[
    int,
    Path(
        ge=1,
        description="Номер сотрудника",
    ),
]


@router.get(
    "",
    response_model=list[EmployeePublicResponse],
    summary="Список сотрудников",
)
def get_employees(
    db: DbSession,
    _current_user: StaffUser,
    include_inactive: Annotated[
        bool,
        Query(),
    ] = False,
) -> list[EmployeePublicResponse]:
    employees = list_employees(
        db,
        include_inactive=include_inactive,
    )

    return [employee_public_response(employee) for employee in employees]


@router.get(
    "/financial",
    response_model=list[EmployeeFinancialResponse],
    summary="Сотрудники со ставками — только владелец",
)
def get_employees_financial(
    db: DbSession,
    _current_user: OwnerOnly,
    include_inactive: Annotated[
        bool,
        Query(),
    ] = False,
) -> list[EmployeeFinancialResponse]:
    employees = list_employees(
        db,
        include_inactive=include_inactive,
    )

    return [
        employee_financial_response(
            db,
            employee,
        )
        for employee in employees
    ]


@router.post(
    "",
    response_model=EmployeeFinancialResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать сотрудника",
)
def add_employee(
    payload: EmployeeCreate,
    db: DbSession,
    _current_user: OwnerOnly,
) -> EmployeeFinancialResponse:
    return create_employee(
        db,
        payload,
    )


@router.put(
    "/{employee_number}",
    response_model=EmployeeFinancialResponse,
    summary="Изменить сотрудника",
)
def edit_employee(
    employee_number: EmployeeNumber,
    payload: EmployeeUpdate,
    db: DbSession,
    _current_user: OwnerOnly,
) -> EmployeeFinancialResponse:
    employee = require_employee(
        db,
        employee_number,
    )

    return update_employee(
        db,
        employee=employee,
        payload=payload,
    )


@router.patch(
    "/{employee_number}/rate",
    response_model=EmployeeFinancialResponse,
    summary="Изменить процентную ставку — только владелец",
)
def edit_employee_rate(
    employee_number: EmployeeNumber,
    payload: EmployeeRateUpdate,
    db: DbSession,
    _current_user: OwnerOnly,
) -> EmployeeFinancialResponse:
    employee = require_employee(
        db,
        employee_number,
    )

    return change_employee_rate(
        db,
        employee=employee,
        rate_percent=payload.rate_percent,
    )


@router.get(
    "/{employee_number}/rates",
    response_model=EmployeeRateHistoryResponse,
    summary="История ставок — только владелец",
)
def get_employee_rate_history(
    employee_number: EmployeeNumber,
    db: DbSession,
    _current_user: OwnerOnly,
) -> EmployeeRateHistoryResponse:
    employee = require_employee(
        db,
        employee_number,
    )

    return employee_rate_history(
        db,
        employee,
    )
