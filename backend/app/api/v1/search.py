from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import DbSession, StaffUser
from app.schemas.search import GlobalSearchResponse
from app.services.search import global_search

router = APIRouter(
    prefix="/search",
    tags=["search"],
)


@router.get(
    "",
    response_model=GlobalSearchResponse,
    summary="Единый поиск по СТО",
)
def search(
    db: DbSession,
    _current_user: StaffUser,
    q: Annotated[
        str,
        Query(
            min_length=1,
            max_length=200,
            description=(
                "ФИО, телефон, номер клиента, госномер, VIN, марка, модель или номер автомобиля"
            ),
        ),
    ],
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=50,
            description="Максимум результатов каждого типа",
        ),
    ] = 20,
) -> GlobalSearchResponse:
    return global_search(
        db,
        query=q,
        limit=limit,
    )
