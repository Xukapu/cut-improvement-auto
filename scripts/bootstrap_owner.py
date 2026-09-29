from getpass import getpass

from app.core.security import hash_password, normalize_login
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from sqlalchemy import select


def main() -> None:
    """Создаёт первого владельца системы."""

    full_name = "Андрей Кузлякин"

    print("Создание первого владельца ЦУТ Improvement Auto")
    print(f"ФИО: {full_name}")

    login_input = input("Введите логин для Андрея: ")
    login = normalize_login(login_input)

    password = getpass("Введите пароль: ")
    password_repeat = getpass("Повторите пароль: ")

    if password != password_repeat:
        raise SystemExit("Пароли не совпадают. Пользователь не создан.")

    password_hash = hash_password(password)

    with SessionLocal() as db:
        existing_user = db.scalar(select(User).where(User.login == login))

        if existing_user is not None:
            raise SystemExit(f"Пользователь с логином '{login}' уже существует.")

        owner_exists = db.scalar(
            select(User).where(
                User.role == UserRole.OWNER,
                User.deleted_at.is_(None),
            )
        )

        if owner_exists is not None:
            raise SystemExit(
                "В системе уже существует владелец. "
                "Автоматическое создание второго владельца запрещено."
            )

        user = User(
            full_name=full_name,
            login=login,
            password_hash=password_hash,
            role=UserRole.OWNER,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print()
        print("Владелец создан успешно.")
        print(f"ID: {user.id}")
        print(f"ФИО: {user.full_name}")
        print(f"Логин: {user.login}")
        print(f"Роль: {user.role.value}")


if __name__ == "__main__":
    main()
