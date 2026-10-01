from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    hash_session_token,
    normalize_login,
    verify_password,
)
from app.models.employee import Employee, EmployeeRate
from app.models.user import User, UserRole
from app.models.user_session import UserSession
from app.schemas.account import (
    EmployeeAccessCreate,
    EmployeeAccessResponse,
    EmployeeAccessUpdate,
    ProfileResponse,
    ProfileUpdate,
)


class AccountError(Exception):
    """Базовая ошибка управления профилем и доступом."""


class EmployeeNotFoundError(AccountError):
    """Сотрудник не найден."""


class AccessNotFoundError(AccountError):
    """У сотрудника нет учётной записи."""


class DuplicateLoginError(AccountError):
    """Такой логин уже используется."""


class LastOwnerError(AccountError):
    """Нельзя отключить последнего владельца."""


class EmployeeInactiveError(AccountError):
    """Нельзя дать доступ неактивному сотруднику."""


class AccessDataRequiredError(AccountError):
    """Недостаточно данных для создания доступа."""


class InvalidCurrentPasswordError(AccountError):
    """Текущий пароль не совпадает."""


class ProtectedRoleError(AccountError):
    """Служебную роль нельзя назначать через интерфейс."""


def split_full_name(
    full_name: str,
) -> tuple[str, str]:
    cleaned = " ".join(full_name.strip().split())

    if not cleaned:
        return "Пользователь", ""

    parts = cleaned.split(" ", 1)

    if len(parts) == 1:
        return parts[0], ""

    return parts[0], parts[1]


def profile_response(
    user: User,
) -> ProfileResponse:
    fallback_first, fallback_last = split_full_name(user.full_name)

    return ProfileResponse(
        first_name=(user.first_name or fallback_first),
        last_name=(user.last_name if user.last_name is not None else fallback_last),
        phone=user.phone,
        login=user.login,
        role=user.role,
        full_name=user.full_name,
    )


def update_profile(
    db: Session,
    *,
    user: User,
    payload: ProfileUpdate,
) -> ProfileResponse:
    full_name = (f"{payload.first_name} {payload.last_name}").strip()

    user.first_name = payload.first_name
    user.last_name = payload.last_name
    user.full_name = full_name
    user.phone = payload.phone

    if user.employee_id is not None:
        employee = db.get(
            Employee,
            user.employee_id,
        )

        if employee is not None:
            employee.full_name = full_name

    db.commit()
    db.refresh(user)

    return profile_response(user)


def revoke_other_sessions(
    db: Session,
    *,
    user_id: UUID,
    current_token: str | None,
) -> None:
    now = datetime.now(UTC)

    statement = (
        update(UserSession)
        .where(
            UserSession.user_id == user_id,
            UserSession.revoked_at.is_(None),
        )
        .values(revoked_at=now)
    )

    if current_token:
        statement = statement.where(UserSession.token_hash != hash_session_token(current_token))

    db.execute(statement)


def revoke_all_sessions(
    db: Session,
    *,
    user_id: UUID,
) -> None:
    db.execute(
        update(UserSession)
        .where(
            UserSession.user_id == user_id,
            UserSession.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(UTC))
    )


def change_own_password(
    db: Session,
    *,
    user: User,
    current_password: str,
    new_password: str,
    current_token: str | None,
) -> None:
    if not verify_password(
        current_password,
        user.password_hash,
    ):
        raise InvalidCurrentPasswordError

    user.password_hash = hash_password(new_password)

    user.password_changed_at = datetime.now(UTC)

    user.failed_login_attempts = 0
    user.locked_until = None

    revoke_other_sessions(
        db,
        user_id=user.id,
        current_token=current_token,
    )

    db.commit()


def _get_employee(
    db: Session,
    employee_number: int,
    *,
    include_archived: bool = False,
) -> Employee:
    conditions = [
        Employee.employee_number == employee_number,
    ]

    if not include_archived:
        conditions.append(Employee.deleted_at.is_(None))

    employee = db.scalar(select(Employee).where(*conditions))

    if employee is None:
        raise EmployeeNotFoundError

    return employee


def _get_user_for_employee(
    db: Session,
    employee: Employee,
) -> User | None:
    return db.scalar(
        select(User).where(
            User.employee_id == employee.id,
            User.deleted_at.is_(None),
        )
    )


def _get_current_rate(
    db: Session,
    employee: Employee,
) -> EmployeeRate | None:
    return db.scalar(
        select(EmployeeRate).where(
            EmployeeRate.employee_id == employee.id,
            EmployeeRate.effective_to.is_(None),
            EmployeeRate.deleted_at.is_(None),
        )
    )


def _set_employee_rate(
    db: Session,
    *,
    employee: Employee,
    rate_percent: Decimal,
) -> None:
    current = _get_current_rate(
        db,
        employee,
    )

    if current is not None and current.rate_percent == rate_percent:
        return

    now = datetime.now(UTC)

    if current is not None:
        current.effective_to = now

    db.add(
        EmployeeRate(
            employee_id=employee.id,
            rate_percent=rate_percent,
            effective_from=now,
        )
    )


def _login_is_taken(
    db: Session,
    *,
    login: str,
    except_user_id: UUID | None = None,
) -> bool:
    normalized = normalize_login(login)

    statement = select(User.id).where(
        User.login == normalized,
        User.deleted_at.is_(None),
    )

    if except_user_id is not None:
        statement = statement.where(User.id != except_user_id)

    return db.scalar(statement) is not None


def _ensure_owner_survives(
    db: Session,
    *,
    user: User,
    new_role: UserRole,
    new_active: bool,
) -> None:
    if user.role != UserRole.OWNER or not user.is_active:
        return

    if new_role == UserRole.OWNER and new_active:
        return

    other_owner_count = db.scalar(
        select(func.count(User.id)).where(
            User.id != user.id,
            User.role == UserRole.OWNER,
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )
    )

    if not other_owner_count:
        raise LastOwnerError


def _ensure_assignable_role(
    role: UserRole,
) -> None:
    if role == UserRole.TECH_ADMIN:
        raise ProtectedRoleError


def _create_user(
    db: Session,
    *,
    employee: Employee,
    login: str,
    role: UserRole,
    password: str,
    phone: str | None,
) -> User:
    _ensure_assignable_role(role)

    normalized_login = normalize_login(login)

    if _login_is_taken(
        db,
        login=normalized_login,
    ):
        raise DuplicateLoginError

    first_name, last_name = split_full_name(employee.full_name)

    user = User(
        full_name=employee.full_name,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        employee_id=employee.id,
        login=normalized_login,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
        failed_login_attempts=0,
    )

    db.add(user)

    return user


def employee_access_response(
    db: Session,
    employee: Employee,
) -> EmployeeAccessResponse:
    rate = _get_current_rate(
        db,
        employee,
    )

    user = _get_user_for_employee(
        db,
        employee,
    )

    current_rate = rate.rate_percent if rate is not None else Decimal("0")

    archived = employee.deleted_at is not None

    return EmployeeAccessResponse(
        employee_number=(employee.employee_number),
        full_name=employee.full_name,
        is_active=(employee.is_active and not archived),
        archived=archived,
        current_rate_percent=(current_rate),
        access_exists=(user is not None),
        access_enabled=bool(user is not None and user.is_active and not archived),
        user_id=(user.id if user is not None else None),
        login=(user.login if user is not None else None),
        role=(user.role if user is not None else None),
        phone=(user.phone if user is not None else None),
    )


def list_employee_access(
    db: Session,
) -> list[EmployeeAccessResponse]:
    employees = list(db.scalars(select(Employee).order_by(Employee.employee_number.asc())).all())

    return [
        employee_access_response(
            db,
            employee,
        )
        for employee in employees
    ]


def create_employee_access(
    db: Session,
    *,
    payload: EmployeeAccessCreate,
) -> EmployeeAccessResponse:
    _ensure_assignable_role(payload.role)

    employee = Employee(
        full_name=payload.full_name,
        is_active=True,
    )

    db.add(employee)
    db.flush()

    _set_employee_rate(
        db,
        employee=employee,
        rate_percent=(payload.rate_percent),
    )

    if payload.grant_access:
        if not payload.login or not payload.temporary_password:
            raise AccessDataRequiredError

        _create_user(
            db,
            employee=employee,
            login=payload.login,
            role=payload.role,
            password=(payload.temporary_password),
            phone=payload.phone,
        )

    db.commit()
    db.refresh(employee)

    return employee_access_response(
        db,
        employee,
    )


def update_employee_access(
    db: Session,
    *,
    employee_number: int,
    payload: EmployeeAccessUpdate,
) -> EmployeeAccessResponse:
    employee = _get_employee(
        db,
        employee_number,
    )

    user = _get_user_for_employee(
        db,
        employee,
    )

    if payload.role is not None:
        _ensure_assignable_role(payload.role)

    if payload.full_name is not None:
        employee.full_name = payload.full_name

        if user is not None:
            first_name, last_name = split_full_name(payload.full_name)

            user.full_name = payload.full_name

            user.first_name = first_name

            user.last_name = last_name

    if payload.rate_percent is not None:
        _set_employee_rate(
            db,
            employee=employee,
            rate_percent=(payload.rate_percent),
        )

    if payload.is_active is not None:
        employee.is_active = payload.is_active

    if payload.grant_access is True and not employee.is_active:
        raise EmployeeInactiveError

    if user is None:
        if payload.grant_access is True:
            if not payload.login or not payload.temporary_password:
                raise AccessDataRequiredError

            user = _create_user(
                db,
                employee=employee,
                login=payload.login,
                role=(payload.role or UserRole.MECHANIC),
                password=(payload.temporary_password),
                phone=payload.phone,
            )

        db.commit()
        db.refresh(employee)

        return employee_access_response(
            db,
            employee,
        )

    new_role = payload.role if payload.role is not None else user.role

    new_active = user.is_active

    if payload.grant_access is True:
        new_active = True

    if payload.grant_access is False:
        new_active = False

    if payload.is_active is False:
        new_active = False

    _ensure_owner_survives(
        db,
        user=user,
        new_role=new_role,
        new_active=new_active,
    )

    if payload.login is not None:
        normalized_login = normalize_login(payload.login)

        if _login_is_taken(
            db,
            login=normalized_login,
            except_user_id=user.id,
        ):
            raise DuplicateLoginError

        user.login = normalized_login

    if payload.role is not None:
        user.role = payload.role

    if payload.phone is not None:
        user.phone = payload.phone

    if payload.temporary_password is not None:
        user.password_hash = hash_password(payload.temporary_password)

        user.password_changed_at = datetime.now(UTC)

        revoke_all_sessions(
            db,
            user_id=user.id,
        )

    user.is_active = new_active

    if not new_active:
        revoke_all_sessions(
            db,
            user_id=user.id,
        )

    if new_active:
        user.failed_login_attempts = 0
        user.locked_until = None

    db.commit()
    db.refresh(employee)

    return employee_access_response(
        db,
        employee,
    )


def archive_employee(
    db: Session,
    *,
    employee_number: int,
) -> EmployeeAccessResponse:
    employee = _get_employee(
        db,
        employee_number,
    )

    user = _get_user_for_employee(
        db,
        employee,
    )

    if user is not None:
        _ensure_owner_survives(
            db,
            user=user,
            new_role=user.role,
            new_active=False,
        )

        user.is_active = False

        revoke_all_sessions(
            db,
            user_id=user.id,
        )

    now = datetime.now(UTC)

    employee.is_active = False
    employee.deleted_at = now

    db.commit()
    db.refresh(employee)

    return employee_access_response(
        db,
        employee,
    )


def restore_employee(
    db: Session,
    *,
    employee_number: int,
) -> EmployeeAccessResponse:
    employee = _get_employee(
        db,
        employee_number,
        include_archived=True,
    )

    if employee.deleted_at is None:
        return employee_access_response(
            db,
            employee,
        )

    employee.deleted_at = None
    employee.is_active = True

    user = _get_user_for_employee(
        db,
        employee,
    )

    if user is not None:
        user.is_active = False
        user.failed_login_attempts = 0
        user.locked_until = None

    db.commit()
    db.refresh(employee)

    return employee_access_response(
        db,
        employee,
    )


def reset_employee_password(
    db: Session,
    *,
    employee_number: int,
    new_password: str,
) -> None:
    employee = _get_employee(
        db,
        employee_number,
    )

    user = _get_user_for_employee(
        db,
        employee,
    )

    if user is None:
        raise AccessNotFoundError

    user.password_hash = hash_password(new_password)

    user.password_changed_at = datetime.now(UTC)

    user.failed_login_attempts = 0
    user.locked_until = None

    revoke_all_sessions(
        db,
        user_id=user.id,
    )

    db.commit()
