import pytest
from app.api.deps import ensure_user_has_role, require_roles
from app.models.user import User, UserRole
from fastapi import HTTPException


def make_user(role: UserRole) -> User:
    return User(
        full_name="Тестовый пользователь",
        login=f"test-{role.value}",
        password_hash="not-used-in-this-test",
        role=role,
        is_active=True,
    )


def test_owner_is_allowed_for_owner_only_action() -> None:
    user = make_user(UserRole.OWNER)

    result = ensure_user_has_role(
        user,
        frozenset({UserRole.OWNER}),
    )

    assert result is user


def test_mechanic_is_forbidden_for_owner_only_action() -> None:
    user = make_user(UserRole.MECHANIC)

    with pytest.raises(HTTPException) as exc_info:
        ensure_user_has_role(
            user,
            frozenset({UserRole.OWNER}),
        )

    assert exc_info.value.status_code == 403


def test_owner_and_tech_admin_can_share_permission() -> None:
    allowed_roles = frozenset(
        {
            UserRole.OWNER,
            UserRole.TECH_ADMIN,
        }
    )

    owner = make_user(UserRole.OWNER)
    tech_admin = make_user(UserRole.TECH_ADMIN)

    assert ensure_user_has_role(owner, allowed_roles) is owner
    assert ensure_user_has_role(tech_admin, allowed_roles) is tech_admin


def test_admin_is_not_tech_admin() -> None:
    user = make_user(UserRole.ADMIN)

    with pytest.raises(HTTPException) as exc_info:
        ensure_user_has_role(
            user,
            frozenset(
                {
                    UserRole.OWNER,
                    UserRole.TECH_ADMIN,
                }
            ),
        )

    assert exc_info.value.status_code == 403


def test_require_roles_rejects_empty_configuration() -> None:
    with pytest.raises(ValueError):
        require_roles()
