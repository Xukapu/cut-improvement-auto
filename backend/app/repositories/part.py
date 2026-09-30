from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.part import Part


def get_part_by_number(
    db: Session,
    part_number: int,
) -> Part | None:
    return db.scalar(
        select(Part).where(
            Part.part_number == part_number,
            Part.deleted_at.is_(None),
        )
    )


def list_parts_for_order(
    db: Session,
    work_order_id,
) -> list[Part]:
    return list(
        db.scalars(
            select(Part)
            .where(
                Part.work_order_id == work_order_id,
                Part.deleted_at.is_(None),
            )
            .order_by(
                Part.part_number.asc(),
            )
        ).all()
    )
