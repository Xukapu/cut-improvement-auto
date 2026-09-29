from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    generate_session_token,
    hash_session_token,
    normalize_login,
    perform_dummy_password_check,
    verify_password,
)
from app.models.user import User
from app.models.user_session import UserSession

settings = get_settings()


class InvalidCredentialsError(Exception):
    """Логин или пароль не прошли проверку."""


def authenticate_user(
    db: Session,
    *,
    login: str,
    password: str,
    ip_address: str | None,
    user_agent: str | None,
) -> tuple[User, str]:
    """Проверяет данные входа и создаёт серверную сессию."""

    normalized_login = normalize_login(login)
    now = datetime.now(UTC)

    user = db.scalar(
        select(User).where(
            User.login == normalized_login,
            User.deleted_at.is_(None),
        )
    )

    if user is None:
        perform_dummy_password_check(password)
        raise InvalidCredentialsError

    if not user.is_active:
        verify_password(password, user.password_hash)
        raise InvalidCredentialsError

    if user.locked_until is not None and user.locked_until > now:
        verify_password(password, user.password_hash)
        raise InvalidCredentialsError

    if user.locked_until is not None and user.locked_until <= now:
        user.failed_login_attempts = 0
        user.locked_until = None

    if not verify_password(password, user.password_hash):
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= settings.login_max_attempts:
            user.locked_until = now + timedelta(minutes=settings.login_lock_minutes)

        db.commit()
        raise InvalidCredentialsError

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = now

    raw_token = generate_session_token()

    session = UserSession(
        user_id=user.id,
        token_hash=hash_session_token(raw_token),
        expires_at=now + timedelta(hours=settings.session_ttl_hours),
        last_seen_at=now,
        ip_address=ip_address,
        user_agent=user_agent[:500] if user_agent else None,
    )

    db.add(session)
    db.commit()
    db.refresh(user)

    return user, raw_token


def get_user_by_session_token(
    db: Session,
    token: str,
) -> User | None:
    """Возвращает активного пользователя по ключу сессии."""

    now = datetime.now(UTC)
    token_hash = hash_session_token(token)

    return db.scalar(
        select(User)
        .join(
            UserSession,
            UserSession.user_id == User.id,
        )
        .where(
            UserSession.token_hash == token_hash,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > now,
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )
    )


def revoke_session(
    db: Session,
    token: str,
) -> None:
    """Отзывает текущую сессию пользователя."""

    token_hash = hash_session_token(token)

    session = db.scalar(
        select(UserSession).where(
            UserSession.token_hash == token_hash,
            UserSession.revoked_at.is_(None),
        )
    )

    if session is None:
        return

    session.revoked_at = datetime.now(UTC)
    db.commit()
