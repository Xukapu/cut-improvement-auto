from fastapi import APIRouter, HTTPException, Request, Response, status

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.schemas.auth import CurrentUserResponse, LoginRequest, MessageResponse
from app.services.auth import (
    InvalidCredentialsError,
    authenticate_user,
    revoke_session,
)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post(
    "/login",
    response_model=CurrentUserResponse,
    summary="Вход в систему",
)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: DbSession,
) -> CurrentUserResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        user, raw_token = authenticate_user(
            db,
            login=payload.login,
            password=payload.password,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль.",
        ) from exc

    response.set_cookie(
        key=settings.session_cookie_name,
        value=raw_token,
        max_age=settings.session_ttl_hours * 60 * 60,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"

    return CurrentUserResponse.model_validate(user)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Выход из системы",
)
def logout(
    request: Request,
    response: Response,
    db: DbSession,
) -> MessageResponse:
    token = request.cookies.get(settings.session_cookie_name)

    if token:
        revoke_session(db, token)

    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        secure=settings.session_cookie_secure,
        httponly=True,
        samesite="lax",
    )
    response.headers["Cache-Control"] = "no-store"

    return MessageResponse(message="Выход выполнен.")


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Текущий пользователь",
)
def me(
    current_user: CurrentUser,
    response: Response,
) -> CurrentUserResponse:
    response.headers["Cache-Control"] = "no-store"
    return CurrentUserResponse.model_validate(current_user)
