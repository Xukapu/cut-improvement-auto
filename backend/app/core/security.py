import hashlib
import re
import secrets

from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()

_LOGIN_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,99}$")
_MIN_PASSWORD_LENGTH = 12
_MAX_PASSWORD_LENGTH = 128

_DUMMY_PASSWORD_HASH = _password_hash.hash(
    "cut-improvement-auto-dummy-password-for-timing-protection"
)


def normalize_login(login: str) -> str:
    """Нормализует и проверяет логин пользователя."""

    normalized = login.strip().lower()

    if not _LOGIN_PATTERN.fullmatch(normalized):
        raise ValueError(
            "Логин должен содержать 3–100 символов: "
            "латинские буквы, цифры, точку, дефис или подчёркивание."
        )

    return normalized


def validate_new_password(password: str) -> None:
    """Проверяет базовые требования к новому паролю."""

    if len(password) < _MIN_PASSWORD_LENGTH:
        raise ValueError(f"Пароль должен содержать минимум {_MIN_PASSWORD_LENGTH} символов.")

    if len(password) > _MAX_PASSWORD_LENGTH:
        raise ValueError(f"Пароль не должен быть длиннее {_MAX_PASSWORD_LENGTH} символов.")


def hash_password(password: str) -> str:
    """Создаёт Argon2-хеш пароля."""

    validate_new_password(password)
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Проверяет пароль по сохранённому хешу."""

    return _password_hash.verify(password, password_hash)


def perform_dummy_password_check(password: str) -> None:
    """Выравнивает время ответа при попытке входа с неизвестным логином."""

    _password_hash.verify(password, _DUMMY_PASSWORD_HASH)


def generate_session_token() -> str:
    """Создаёт криптографически стойкий ключ сессии."""

    return secrets.token_urlsafe(48)


def hash_session_token(token: str) -> str:
    """Хеширует ключ сессии перед сохранением в базе."""

    return hashlib.sha256(token.encode("utf-8")).hexdigest()
