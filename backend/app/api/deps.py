from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User, UserRole
from app.services.auth import get_user_by_session_token

settings = get_settings()

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    request: Request,
    db: DbSession,
) -> User:
    """Проверяет серверную сессию текущего пользователя."""

    token = request.cookies.get(settings.session_cookie_name)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация.",
        )

    user = get_user_by_session_token(db, token)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Сессия недействительна или завершена.",
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def ensure_user_has_role(
    user: User,
    allowed_roles: frozenset[UserRole],
) -> User:
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции.",
        )

    return user


def require_roles(
    *allowed_roles: UserRole,
) -> Callable[[User], User]:
    roles = frozenset(allowed_roles)

    if not roles:
        raise ValueError("Необходимо указать хотя бы одну разрешённую роль.")

    def dependency(
        current_user: CurrentUser,
    ) -> User:
        return ensure_user_has_role(
            current_user,
            roles,
        )

    return dependency


OwnerOnly = Annotated[
    User,
    Depends(
        require_roles(
            UserRole.OWNER,
        )
    ),
]

OwnerOrTechAdmin = Annotated[
    User,
    Depends(
        require_roles(
            UserRole.OWNER,
            UserRole.TECH_ADMIN,
        )
    ),
]

ManagerUser = Annotated[
    User,
    Depends(
        require_roles(
            UserRole.OWNER,
            UserRole.TECH_ADMIN,
            UserRole.ADMIN,
        )
    ),
]

StaffUser = Annotated[
    User,
    Depends(
        require_roles(
            UserRole.OWNER,
            UserRole.TECH_ADMIN,
            UserRole.ADMIN,
            UserRole.MECHANIC,
        )
    ),
]
