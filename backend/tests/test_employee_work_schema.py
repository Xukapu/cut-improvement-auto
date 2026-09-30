from decimal import Decimal

import pytest
from app.schemas.employee import EmployeeCreate
from app.schemas.work_item import WorkItemCreate
from pydantic import ValidationError


def test_employee_create() -> None:
    employee = EmployeeCreate(
        full_name="Иван Механик",
        rate_percent=Decimal("30"),
    )

    assert employee.rate_percent == Decimal("30")


def test_employee_rate_cannot_exceed_100() -> None:
    with pytest.raises(ValidationError):
        EmployeeCreate(
            full_name="Иван Механик",
            rate_percent=Decimal("101"),
        )


def test_work_assignments_must_total_100() -> None:
    with pytest.raises(ValidationError):
        WorkItemCreate(
            name="Замена масла",
            price=Decimal("10000"),
            assignments=[
                {
                    "employee_number": 1,
                    "share_percent": Decimal("70"),
                },
                {
                    "employee_number": 2,
                    "share_percent": Decimal("20"),
                },
            ],
        )


def test_work_accepts_multiple_employees_at_100_percent() -> None:
    work = WorkItemCreate(
        name="Замена масла",
        price=Decimal("10000"),
        assignments=[
            {
                "employee_number": 1,
                "share_percent": Decimal("70"),
            },
            {
                "employee_number": 2,
                "share_percent": Decimal("30"),
            },
        ],
    )

    assert sum(assignment.share_percent for assignment in work.assignments) == Decimal("100")


def test_duplicate_employee_is_rejected() -> None:
    with pytest.raises(ValidationError):
        WorkItemCreate(
            name="Замена масла",
            price=Decimal("10000"),
            assignments=[
                {
                    "employee_number": 1,
                    "share_percent": Decimal("50"),
                },
                {
                    "employee_number": 1,
                    "share_percent": Decimal("50"),
                },
            ],
        )
