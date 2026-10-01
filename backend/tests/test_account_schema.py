from decimal import Decimal

import pytest
from app.models.user import UserRole
from app.schemas.account import (
    EmployeeAccessCreate,
    EmployeeAccessUpdate,
    PasswordChange,
    ProfileUpdate,
)
from pydantic import ValidationError


def test_profile_update() -> None:
    profile = ProfileUpdate(
        first_name=" Андрей ",
        last_name=" Кузлякин ",
        phone=" +7 900 000-00-00 ",
    )

    assert profile.first_name == "Андрей"
    assert profile.last_name == "Кузлякин"
    assert profile.phone == "+7 900 000-00-00"


def test_password_change_requires_current_password() -> None:
    payload = PasswordChange(
        current_password="old-password",
        new_password="new-password-123",
    )

    assert payload.current_password == "old-password"
    assert payload.new_password == "new-password-123"


def test_new_password_requires_twelve_characters() -> None:
    with pytest.raises(ValidationError):
        PasswordChange(
            current_password="old-password",
            new_password="short",
        )


def test_new_employee_can_exist_without_login() -> None:
    employee = EmployeeAccessCreate(
        full_name="Иван Механик",
        rate_percent=Decimal("30"),
        grant_access=False,
    )

    assert employee.grant_access is False


def test_access_requires_login_and_password() -> None:
    with pytest.raises(ValidationError):
        EmployeeAccessCreate(
            full_name="Иван Механик",
            rate_percent=Decimal("30"),
            grant_access=True,
            role=UserRole.MECHANIC,
        )


def test_access_accepts_valid_credentials() -> None:
    employee = EmployeeAccessCreate(
        full_name="Иван Механик",
        rate_percent=Decimal("30"),
        grant_access=True,
        login=" IVAN ",
        role=UserRole.MECHANIC,
        temporary_password="temporary-12345",
    )

    assert employee.login == "ivan"


def test_tech_admin_cannot_be_assigned_on_create() -> None:
    with pytest.raises(ValidationError):
        EmployeeAccessCreate(
            full_name="Служебный пользователь",
            rate_percent=Decimal("0"),
            grant_access=False,
            role=UserRole.TECH_ADMIN,
        )


def test_tech_admin_cannot_be_assigned_on_update() -> None:
    with pytest.raises(ValidationError):
        EmployeeAccessUpdate(
            role=UserRole.TECH_ADMIN,
        )
