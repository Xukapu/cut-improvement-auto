from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import DbSession, OwnerOnly
from app.schemas.audit import AuditLogListResponse
from app.services.audit import get_audit_log

_SUMMARY_AUDIT = (
    "\u0416\u0443\u0440\u043d\u0430\u043b \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0439"
)


router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)

OptionalEntityType = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=64,
    ),
]

OptionalEntityNumber = Annotated[
    int | None,
    Query(ge=1),
]

OptionalAction = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=64,
    ),
]

OptionalActorLogin = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=100,
    ),
]

OptionalDate = Annotated[
    date | None,
    Query(),
]

Limit = Annotated[
    int,
    Query(
        ge=1,
        le=200,
    ),
]

Offset = Annotated[
    int,
    Query(ge=0),
]


@router.get(
    "",
    response_model=AuditLogListResponse,
    summary=_SUMMARY_AUDIT,
)
def audit_log(
    db: DbSession,
    _current_user: OwnerOnly,
    entity_type: OptionalEntityType = None,
    entity_number: OptionalEntityNumber = None,
    action: OptionalAction = None,
    actor_login: OptionalActorLogin = None,
    date_from: OptionalDate = None,
    date_to: OptionalDate = None,
    limit: Limit = 100,
    offset: Offset = 0,
) -> AuditLogListResponse:
    return get_audit_log(
        db,
        entity_type=entity_type,
        entity_number=entity_number,
        action=action,
        actor_login=actor_login,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
