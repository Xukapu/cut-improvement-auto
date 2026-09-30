from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recommended_work import RecommendedWork


def get_recommended_work_by_number(
    db: Session,
    recommended_work_number: int,
) -> RecommendedWork | None:
    return db.scalar(
        select(RecommendedWork).where(
            RecommendedWork.recommended_work_number == recommended_work_number,
            RecommendedWork.deleted_at.is_(None),
        )
    )


def list_recommended_works_for_order(
    db: Session,
    work_order_id: UUID,
) -> list[RecommendedWork]:
    return list(
        db.scalars(
            select(RecommendedWork)
            .where(
                RecommendedWork.work_order_id == work_order_id,
                RecommendedWork.deleted_at.is_(None),
            )
            .order_by(
                RecommendedWork.recommended_work_number.asc(),
            )
        ).all()
    )
