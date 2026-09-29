import app.models  # noqa: F401
from app.db.base import Base
from sqlalchemy import CheckConstraint


def test_core_tables_are_registered() -> None:
    assert {
        "app_users",
        "clients",
        "vehicles",
        "client_vehicles",
        "user_sessions",
    }.issubset(Base.metadata.tables)


def test_user_role_has_one_check_constraint() -> None:
    table = Base.metadata.tables["app_users"]

    checks = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint) and "role IN" in str(constraint.sqltext)
    ]

    assert len(checks) == 1


def test_client_source_has_one_check_constraint() -> None:
    table = Base.metadata.tables["clients"]

    checks = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint) and "source IN" in str(constraint.sqltext)
    ]

    assert len(checks) == 1


def test_user_login_is_forced_to_lowercase() -> None:
    table = Base.metadata.tables["app_users"]

    checks = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
        and "login = lower(login)" in str(constraint.sqltext)
    ]

    assert len(checks) == 1


def test_login_attempts_cannot_be_negative() -> None:
    table = Base.metadata.tables["app_users"]

    checks = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
        and "failed_login_attempts >= 0" in str(constraint.sqltext)
    ]

    assert len(checks) == 1


def test_session_expiration_is_validated() -> None:
    table = Base.metadata.tables["user_sessions"]

    checks = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
        and "expires_at > created_at" in str(constraint.sqltext)
    ]

    assert len(checks) == 1
