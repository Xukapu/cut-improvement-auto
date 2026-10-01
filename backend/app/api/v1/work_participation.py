from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession, OwnerOnly
from app.schemas.work_participation import (
    WorkParticipationResponse,
    WorkParticipationUpdate,
)
from app.services.work_participation import (
    get_work_participation,
    update_work_participation,
)

router = APIRouter(
    prefix="/account/work-participation",
    tags=["account"],
)


@router.get(
    "",
    response_model=WorkParticipationResponse,
    summary="Моё участие в работах СТО",
)
def my_work_participation(
    db: DbSession,
    current_user: OwnerOnly,
) -> WorkParticipationResponse:
    return get_work_participation(
        db,
        user=current_user,
    )


@router.put(
    "",
    response_model=WorkParticipationResponse,
    summary="Настроить участие в работах СТО",
)
def edit_work_participation(
    payload: WorkParticipationUpdate,
    db: DbSession,
    current_user: OwnerOnly,
) -> WorkParticipationResponse:
    try:
        return update_work_participation(
            db,
            user=current_user,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
