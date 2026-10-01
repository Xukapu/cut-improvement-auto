from typing import Annotated

from fastapi import (
    APIRouter,
    HTTPException,
    Path,
    Request,
    status,
)

from app.api.deps import (
    CurrentUser,
    DbSession,
    OwnerOnly,
)
from app.core.config import get_settings
from app.schemas.account import (
    EmployeeAccessCreate,
    EmployeeAccessResponse,
    EmployeeAccessUpdate,
    EmployeePasswordReset,
    PasswordChange,
    ProfileResponse,
    ProfileUpdate,
)
from app.schemas.auth import MessageResponse
from app.services.account import (
    AccessDataRequiredError,
    AccessNotFoundError,
    DuplicateLoginError,
    EmployeeInactiveError,
    EmployeeNotFoundError,
    InvalidCurrentPasswordError,
    LastOwnerError,
    ProtectedRoleError,
    archive_employee,
    change_own_password,
    create_employee_access,
    list_employee_access,
    profile_response,
    reset_employee_password,
    restore_employee,
    update_employee_access,
    update_profile,
)

router = APIRouter(
    prefix="/account",
    tags=["account"],
)

settings = get_settings()

EmployeeNumber = Annotated[
    int,
    Path(ge=1),
]


def _raise_account_error(
    exc: Exception,
) -> None:
    if isinstance(
        exc,
        EmployeeNotFoundError,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден.",
        ) from exc

    if isinstance(
        exc,
        AccessNotFoundError,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=("У сотрудника нет учётной записи."),
        ) from exc

    if isinstance(
        exc,
        DuplicateLoginError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Этот логин уже используется."),
        ) from exc

    if isinstance(
        exc,
        LastOwnerError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Нельзя отключить или удалить последнего активного владельца."),
        ) from exc

    if isinstance(
        exc,
        EmployeeInactiveError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Нельзя включить доступ неактивному сотруднику."),
        ) from exc

    if isinstance(
        exc,
        AccessDataRequiredError,
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("Для нового доступа нужны логин и временный пароль."),
        ) from exc

    if isinstance(
        exc,
        ProtectedRoleError,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Технический администратор — "
                "служебная роль и не назначается "
                "через интерфейс сотрудников."
            ),
        ) from exc

    raise exc


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="Мой профиль",
)
def get_profile(
    current_user: CurrentUser,
) -> ProfileResponse:
    return profile_response(current_user)


@router.put(
    "/profile",
    response_model=ProfileResponse,
    summary="Изменить мой профиль",
)
def edit_profile(
    payload: ProfileUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ProfileResponse:
    return update_profile(
        db,
        user=current_user,
        payload=payload,
    )


@router.put(
    "/password",
    response_model=MessageResponse,
    summary="Изменить мой пароль",
)
def edit_my_password(
    payload: PasswordChange,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> MessageResponse:
    token = request.cookies.get(settings.session_cookie_name)

    try:
        change_own_password(
            db,
            user=current_user,
            current_password=(payload.current_password),
            new_password=(payload.new_password),
            current_token=token,
        )
    except InvalidCurrentPasswordError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("Текущий пароль указан неверно."),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return MessageResponse(message=("Пароль изменён. Остальные сессии завершены."))


@router.get(
    "/employees",
    response_model=list[EmployeeAccessResponse],
    summary="Сотрудники и доступ",
)
def get_employee_access(
    db: DbSession,
    _current_user: OwnerOnly,
) -> list[EmployeeAccessResponse]:
    return list_employee_access(db)


@router.post(
    "/employees",
    response_model=EmployeeAccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать сотрудника",
)
def add_employee_access(
    payload: EmployeeAccessCreate,
    db: DbSession,
    _current_user: OwnerOnly,
) -> EmployeeAccessResponse:
    try:
        return create_employee_access(
            db,
            payload=payload,
        )
    except Exception as exc:
        _raise_account_error(exc)
        raise


@router.put(
    "/employees/{employee_number}",
    response_model=EmployeeAccessResponse,
    summary="Изменить сотрудника и доступ",
)
def edit_employee_access(
    employee_number: EmployeeNumber,
    payload: EmployeeAccessUpdate,
    db: DbSession,
    _current_user: OwnerOnly,
) -> EmployeeAccessResponse:
    try:
        return update_employee_access(
            db,
            employee_number=(employee_number),
            payload=payload,
        )
    except Exception as exc:
        _raise_account_error(exc)
        raise


@router.delete(
    "/employees/{employee_number}",
    response_model=EmployeeAccessResponse,
    summary="Удалить сотрудника в архив",
)
def delete_employee(
    employee_number: EmployeeNumber,
    db: DbSession,
    _current_user: OwnerOnly,
) -> EmployeeAccessResponse:
    try:
        return archive_employee(
            db,
            employee_number=(employee_number),
        )
    except Exception as exc:
        _raise_account_error(exc)
        raise


@router.post(
    "/employees/{employee_number}/restore",
    response_model=EmployeeAccessResponse,
    summary="Восстановить сотрудника из архива",
)
def restore_archived_employee(
    employee_number: EmployeeNumber,
    db: DbSession,
    _current_user: OwnerOnly,
) -> EmployeeAccessResponse:
    try:
        return restore_employee(
            db,
            employee_number=(employee_number),
        )
    except Exception as exc:
        _raise_account_error(exc)
        raise


@router.post(
    "/employees/{employee_number}/reset-password",
    response_model=MessageResponse,
    summary="Сбросить пароль сотрудника",
)
def reset_password(
    employee_number: EmployeeNumber,
    payload: EmployeePasswordReset,
    db: DbSession,
    _current_user: OwnerOnly,
) -> MessageResponse:
    try:
        reset_employee_password(
            db,
            employee_number=(employee_number),
            new_password=(payload.new_password),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        _raise_account_error(exc)
        raise

    return MessageResponse(message=("Пароль сотрудника изменён. Все его старые сессии завершены."))
