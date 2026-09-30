from typing import Annotated

from fastapi import APIRouter, Path, Response

from app.api.deps import DbSession, StaffUser
from app.schemas.document import WorkOrderDocumentData
from app.services.document import (
    build_completion_act_pdf,
    build_work_order_pdf,
    get_work_order_document_data,
)

router = APIRouter(
    prefix="/work-orders",
    tags=["documents"],
)

PositiveNumber = Annotated[
    int,
    Path(ge=1),
]


@router.get(
    "/{work_order_number}/documents/data",
    response_model=WorkOrderDocumentData,
    summary="Данные печатных документов",
)
def document_data(
    work_order_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> WorkOrderDocumentData:
    return get_work_order_document_data(
        db,
        work_order_number,
    )


@router.get(
    "/{work_order_number}/documents/work-order.pdf",
    summary="PDF заказ-наряда",
    responses={
        200: {
            "content": {
                "application/pdf": {},
            }
        }
    },
)
def work_order_pdf(
    work_order_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> Response:
    data = get_work_order_document_data(
        db,
        work_order_number,
    )

    content = build_work_order_pdf(data)

    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (f'inline; filename="work_order_{work_order_number}.pdf"'),
        },
    )


@router.get(
    "/{work_order_number}/documents/completion-act.pdf",
    summary="PDF акта выполненных работ",
    responses={
        200: {
            "content": {
                "application/pdf": {},
            }
        }
    },
)
def completion_act_pdf(
    work_order_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> Response:
    data = get_work_order_document_data(
        db,
        work_order_number,
    )

    content = build_completion_act_pdf(data)

    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (f'inline; filename="completion_act_{work_order_number}.pdf"'),
        },
    )
