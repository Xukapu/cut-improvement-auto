from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.recommended_work import RecommendedWork
from app.models.work_order import WorkOrderStatus
from app.repositories.recommended_work import (
    get_recommended_work_by_number,
    list_recommended_works_for_order,
)
from app.schemas.recommended_work import (
    RecommendedWorkListResponse,
    RecommendedWorkResponse,
    RecommendedWorkWrite,
)
from app.services.work_order import require_work_order


def ensure_recommendations_editable(order) -> None:
    if order.status == WorkOrderStatus.ISSUED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Нельзя изменять рекомендованные работы в выданном заказ-наряде."),
        )


def require_order_recommended_work(
    db: Session,
    *,
    order,
    recommended_work_number: int,
) -> RecommendedWork:
    recommended_work = get_recommended_work_by_number(
        db,
        recommended_work_number,
    )

    if recommended_work is None or recommended_work.work_order_id != order.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=("Рекомендованная работа в этом заказ-наряде не найдена."),
        )

    return recommended_work


def create_recommended_work(
    db: Session,
    *,
    work_order_number: int,
    payload: RecommendedWorkWrite,
) -> RecommendedWorkResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    ensure_recommendations_editable(order)

    recommended_work = RecommendedWork(
        work_order_id=order.id,
        name=payload.name,
        comment=payload.comment,
    )

    db.add(recommended_work)
    db.commit()
    db.refresh(recommended_work)

    return RecommendedWorkResponse.model_validate(recommended_work)


def update_recommended_work(
    db: Session,
    *,
    work_order_number: int,
    recommended_work_number: int,
    payload: RecommendedWorkWrite,
) -> RecommendedWorkResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    ensure_recommendations_editable(order)

    recommended_work = require_order_recommended_work(
        db,
        order=order,
        recommended_work_number=recommended_work_number,
    )

    recommended_work.name = payload.name
    recommended_work.comment = payload.comment

    db.commit()
    db.refresh(recommended_work)

    return RecommendedWorkResponse.model_validate(recommended_work)


def delete_recommended_work(
    db: Session,
    *,
    work_order_number: int,
    recommended_work_number: int,
) -> None:
    order = require_work_order(
        db,
        work_order_number,
    )

    ensure_recommendations_editable(order)

    recommended_work = require_order_recommended_work(
        db,
        order=order,
        recommended_work_number=recommended_work_number,
    )

    recommended_work.deleted_at = datetime.now(UTC)

    db.commit()


def get_order_recommended_works(
    db: Session,
    work_order_number: int,
) -> RecommendedWorkListResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    recommended_works = list_recommended_works_for_order(
        db,
        order.id,
    )

    return RecommendedWorkListResponse(
        items=[RecommendedWorkResponse.model_validate(item) for item in recommended_works],
        total=len(recommended_works),
    )
