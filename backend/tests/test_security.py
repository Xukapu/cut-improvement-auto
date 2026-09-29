import pytest
from app.core.security import (
    generate_session_token,
    hash_password,
    hash_session_token,
    normalize_login,
    validate_new_password,
    verify_password,
)


def test_password_is_hashed_and_verified() -> None:
    password = "correct horse battery staple"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)
    assert not verify_password("wrong password", password_hash)


def test_short_password_is_rejected() -> None:
    with pytest.raises(ValueError):
        validate_new_password("short")


def test_login_is_normalized() -> None:
    assert normalize_login("  Andrey.Kuzlyakin  ") == "andrey.kuzlyakin"


@pytest.mark.parametrize(
    "login",
    [
        "ab",
        "андрей",
        "user name",
        "@andrey",
    ],
)
def test_invalid_login_is_rejected(login: str) -> None:
    with pytest.raises(ValueError):
        normalize_login(login)


def test_session_tokens_are_random_and_hashed() -> None:
    token_one = generate_session_token()
    token_two = generate_session_token()

    assert token_one != token_two
    assert hash_session_token(token_one) != token_one
    assert len(hash_session_token(token_one)) == 64
