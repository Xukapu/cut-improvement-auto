from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import DbSession, StaffUser
from app.schemas.report import DashboardResponse
from app.services.report import get_dashboard

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
)

OptionalDate = Annotated[
    date | None,
    Query(),
]


@router.get(
    "",
    response_model=DashboardResponse,
    summary="Главная страница",
)
def dashboard(
    db: DbSession,
    _current_user: StaffUser,
    report_date: OptionalDate = None,
) -> DashboardResponse:
    return get_dashboard(
        db,
        report_date=report_date,
    )
