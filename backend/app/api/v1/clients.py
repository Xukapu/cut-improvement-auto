from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status

from app.api.deps import (
    DbSession,
    ManagerUser,
    OwnerOnly,
    OwnerOrTechAdmin,
    StaffUser,
)
from app.models.user import UserRole
from app.repositories.client import (
    get_archived_client_by_number,
    get_client_by_number,
    list_archived_clients,
    list_clients,
)
from app.schemas.client import (
    ArchiveClientRequest,
    ArchivedClientListResponse,
    ArchivedClientResponse,
    ClientCreate,
    ClientInternalMarkUpdate,
    ClientListResponse,
    ClientResponse,
    ClientUpdate,
)
from app.services.client import (
    archive_client,
    create_client,
    restore_client,
    set_client_internal_mark,
    update_client,
)

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)

ClientNumber = Annotated[
    int,
    Path(
        ge=1,
        description="Номер клиента",
    ),
]


@router.get(
    "",
    response_model=ClientListResponse,
    summary="Список и поиск активных клиентов",
)
def get_clients(
    db: DbSession,
    _current_user: StaffUser,
    search: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=200,
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
        ),
    ] = 50,
    offset: Annotated[
        int,
        Query(
            ge=0,
        ),
    ] = 0,
) -> ClientListResponse:
    clients, total = list_clients(
        db,
        search=search,
        limit=limit,
        offset=offset,
    )

    return ClientListResponse(
        items=[ClientResponse.model_validate(client) for client in clients],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/archive",
    response_model=ArchivedClientListResponse,
    summary="Архив клиентов",
)
def get_archive(
    db: DbSession,
    _current_user: StaffUser,
    search: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=200,
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
        ),
    ] = 50,
    offset: Annotated[
        int,
        Query(
            ge=0,
        ),
    ] = 0,
) -> ArchivedClientListResponse:
    clients, total = list_archived_clients(
        db,
        search=search,
        limit=limit,
        offset=offset,
    )

    return ArchivedClientListResponse(
        items=[ArchivedClientResponse.model_validate(client) for client in clients],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/archive/{client_number}",
    response_model=ArchivedClientResponse,
    summary="Карточка клиента из архива",
)
def get_archived_client(
    client_number: ClientNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> ArchivedClientResponse:
    client = get_archived_client_by_number(
        db,
        client_number,
    )

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент в архиве не найден.",
        )

    return ArchivedClientResponse.model_validate(client)


@router.get(
    "/{client_number}",
    response_model=ClientResponse,
    summary="Карточка активного клиента",
)
def get_client(
    client_number: ClientNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> ClientResponse:
    client = get_client_by_number(
        db,
        client_number,
    )

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден.",
        )

    return ClientResponse.model_validate(client)


@router.post(
    "",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать клиента",
)
def add_client(
    payload: ClientCreate,
    db: DbSession,
    current_user: ManagerUser,
) -> ClientResponse:
    if payload.internal_mark and current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=("Внутреннюю метку клиента может устанавливать только владелец."),
        )

    client = create_client(
        db,
        payload,
    )

    return ClientResponse.model_validate(client)


@router.put(
    "/{client_number}",
    response_model=ClientResponse,
    summary="Изменить клиента",
)
def edit_client(
    client_number: ClientNumber,
    payload: ClientUpdate,
    db: DbSession,
    _current_user: ManagerUser,
) -> ClientResponse:
    client = get_client_by_number(
        db,
        client_number,
    )

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден.",
        )

    updated = update_client(
        db,
        client=client,
        payload=payload,
    )

    return ClientResponse.model_validate(updated)


@router.patch(
    "/{client_number}/internal-mark",
    response_model=ClientResponse,
    summary="Поставить или снять внутреннюю метку клиента",
)
def edit_client_internal_mark(
    client_number: ClientNumber,
    payload: ClientInternalMarkUpdate,
    db: DbSession,
    _current_user: OwnerOnly,
) -> ClientResponse:
    client = get_client_by_number(
        db,
        client_number,
    )

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден.",
        )

    updated = set_client_internal_mark(
        db,
        client=client,
        internal_mark=payload.internal_mark,
    )

    return ClientResponse.model_validate(updated)


@router.post(
    "/{client_number}/archive",
    response_model=ArchivedClientResponse,
    summary="Переместить клиента в архив",
)
def move_client_to_archive(
    client_number: ClientNumber,
    payload: ArchiveClientRequest,
    db: DbSession,
    current_user: OwnerOrTechAdmin,
) -> ArchivedClientResponse:
    client = get_client_by_number(
        db,
        client_number,
    )

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден.",
        )

    archived = archive_client(
        db,
        client=client,
        actor_user_id=current_user.id,
        reason=payload.reason,
        comment=payload.comment,
    )

    return ArchivedClientResponse.model_validate(archived)


@router.post(
    "/{client_number}/restore",
    response_model=ClientResponse,
    summary="Восстановить клиента из архива",
)
def restore_client_from_archive(
    client_number: ClientNumber,
    db: DbSession,
    _current_user: OwnerOrTechAdmin,
) -> ClientResponse:
    client = get_archived_client_by_number(
        db,
        client_number,
    )

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент в архиве не найден.",
        )

    restored = restore_client(
        db,
        client,
    )

    return ClientResponse.model_validate(restored)
