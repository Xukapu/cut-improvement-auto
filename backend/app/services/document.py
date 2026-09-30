# ruff: noqa: E501
import os
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from html import escape
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, status
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.part import Part
from app.models.recommended_work import RecommendedWork
from app.models.vehicle import Vehicle
from app.models.work_item import WorkItem
from app.schemas.document import (
    DocumentClient,
    DocumentPart,
    DocumentPayment,
    DocumentRecommendation,
    DocumentVehicle,
    DocumentWork,
    WorkOrderDocumentData,
)
from app.services.payment import (
    calculate_paid_amount,
    calculate_repair_total,
)
from app.services.work_order import require_work_order

_MONEY = Decimal("0.01")

_FONT_REGULAR = "CutAutoRegular"
_FONT_BOLD = "CutAutoBold"

_fonts_registered = False

COMPANY_NAME = "\u0426\u0423\u0422 Improvement Auto"

STATUS_LABELS = {
    "planned": "\u0417\u0430\u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d",
    "in_progress": "\u0412 \u0440\u0430\u0431\u043e\u0442\u0435",
    "ready": "\u0413\u043e\u0442\u043e\u0432",
    "issued": "\u0412\u044b\u0434\u0430\u043d",
}

PROVIDER_LABELS = {
    "sto": "\u0421\u0422\u041e",
    "client": "\u041a\u043b\u0438\u0435\u043d\u0442",
}


def money(
    value: Decimal | int | float | None,
) -> Decimal:
    if value is None:
        value = Decimal("0")

    if not isinstance(value, Decimal):
        value = Decimal(str(value))

    return value.quantize(
        _MONEY,
        rounding=ROUND_HALF_UP,
    )


def format_date(
    value: date | datetime,
) -> str:
    if isinstance(value, datetime):
        value = value.date()

    return value.strftime("%d.%m.%Y")


def format_money(
    value: Decimal | int | float | None,
) -> str:
    amount = money(value)

    formatted = f"{amount:,.2f}"
    formatted = formatted.replace(",", " ")
    formatted = formatted.replace(".", ",")

    return f"{formatted} \u20bd"


def enum_value(value) -> str:
    return getattr(
        value,
        "value",
        str(value),
    )


def _font_candidates() -> list[tuple[Path, Path]]:
    windir = Path(
        os.environ.get(
            "WINDIR",
            r"C:\Windows",
        )
    )

    return [
        (
            windir / "Fonts" / "arial.ttf",
            windir / "Fonts" / "arialbd.ttf",
        ),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
        (
            Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
            Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
        ),
    ]


def ensure_pdf_fonts() -> None:
    global _fonts_registered

    if _fonts_registered:
        return

    for regular_path, bold_path in _font_candidates():
        if regular_path.is_file() and bold_path.is_file():
            pdfmetrics.registerFont(
                TTFont(
                    _FONT_REGULAR,
                    str(regular_path),
                )
            )

            pdfmetrics.registerFont(
                TTFont(
                    _FONT_BOLD,
                    str(bold_path),
                )
            )

            _fonts_registered = True
            return

    raise RuntimeError(
        "\u041d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d "
        "\u0441\u0438\u0441\u0442\u0435\u043c\u043d\u044b\u0439 "
        "\u0448\u0440\u0438\u0444\u0442 \u0441 "
        "\u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u043e\u0439 "
        "\u043a\u0438\u0440\u0438\u043b\u043b\u0438\u0446\u044b."
    )


def get_work_order_document_data(
    db: Session,
    work_order_number: int,
) -> WorkOrderDocumentData:
    order = require_work_order(
        db,
        work_order_number,
    )

    client = db.get(
        Client,
        order.client_id,
    )

    vehicle = db.get(
        Vehicle,
        order.vehicle_id,
    )

    if client is None or vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c "
                "\u043f\u043e\u043b\u0443\u0447\u0438\u0442\u044c "
                "\u043a\u043b\u0438\u0435\u043d\u0442\u0430 "
                "\u0438\u043b\u0438 \u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044c "
                "\u0437\u0430\u043a\u0430\u0437-\u043d\u0430\u0440\u044f\u0434\u0430."
            ),
        )

    works = list(
        db.scalars(
            select(WorkItem)
            .where(
                WorkItem.work_order_id == order.id,
                WorkItem.deleted_at.is_(None),
            )
            .order_by(
                WorkItem.work_item_number.asc(),
            )
        ).all()
    )

    parts = list(
        db.scalars(
            select(Part)
            .where(
                Part.work_order_id == order.id,
                Part.deleted_at.is_(None),
            )
            .order_by(
                Part.part_number.asc(),
            )
        ).all()
    )

    recommendations = list(
        db.scalars(
            select(RecommendedWork)
            .where(
                RecommendedWork.work_order_id == order.id,
                RecommendedWork.deleted_at.is_(None),
            )
            .order_by(
                RecommendedWork.recommended_work_number.asc(),
            )
        ).all()
    )

    (
        works_total,
        sto_parts_total,
        repair_total,
    ) = calculate_repair_total(
        db,
        order.id,
    )

    paid_amount = calculate_paid_amount(
        db,
        order.id,
    )

    debt_amount = money(repair_total - paid_amount)

    document_source_date = order.issued_at or order.ready_at or order.started_at or order.created_at

    status_value = enum_value(order.status)

    return WorkOrderDocumentData(
        work_order_number=order.work_order_number,
        document_date=format_date(document_source_date),
        status=STATUS_LABELS.get(
            status_value,
            status_value,
        ),
        reason=order.reason,
        client=DocumentClient(
            client_number=client.client_number,
            full_name=client.full_name,
            phone_primary=client.phone_primary,
            phone_secondary=client.phone_secondary,
        ),
        vehicle=DocumentVehicle(
            vehicle_number=vehicle.vehicle_number,
            brand=vehicle.brand,
            model=vehicle.model,
            license_plate=vehicle.license_plate,
            vin=vehicle.vin,
            year=vehicle.year,
            mileage=order.mileage,
        ),
        works=[
            DocumentWork(
                work_item_number=item.work_item_number,
                name=item.name,
                price=money(item.price),
            )
            for item in works
        ],
        parts=[
            DocumentPart(
                part_number=item.part_number,
                name=item.name,
                quantity=item.quantity,
                unit_price=money(item.unit_price),
                total_price=money(item.unit_price * item.quantity),
                supplier=item.supplier,
                provided_by=PROVIDER_LABELS.get(
                    enum_value(item.provided_by),
                    enum_value(item.provided_by),
                ),
            )
            for item in parts
        ],
        recommendations=[
            DocumentRecommendation(
                recommended_work_number=item.recommended_work_number,
                name=item.name,
                comment=item.comment,
            )
            for item in recommendations
        ],
        payment=DocumentPayment(
            works_total=works_total,
            sto_parts_total=sto_parts_total,
            repair_total=repair_total,
            paid_amount=paid_amount,
            debt_amount=debt_amount,
        ),
    )


def _styles() -> dict[str, ParagraphStyle]:
    ensure_pdf_fonts()

    return {
        "company": ParagraphStyle(
            "CompanyName",
            fontName=_FONT_BOLD,
            fontSize=14,
            leading=16,
            alignment=TA_CENTER,
            spaceAfter=2 * mm,
        ),
        "title": ParagraphStyle(
            "DocumentTitle",
            fontName=_FONT_BOLD,
            fontSize=16,
            leading=19,
            alignment=TA_CENTER,
            spaceAfter=1.5 * mm,
        ),
        "document_date": ParagraphStyle(
            "DocumentDate",
            fontName=_FONT_REGULAR,
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            spaceAfter=5 * mm,
        ),
        "heading": ParagraphStyle(
            "DocumentHeading",
            fontName=_FONT_BOLD,
            fontSize=10,
            leading=13,
            spaceBefore=4 * mm,
            spaceAfter=2 * mm,
        ),
        "normal": ParagraphStyle(
            "DocumentNormal",
            fontName=_FONT_REGULAR,
            fontSize=9,
            leading=12,
        ),
        "small": ParagraphStyle(
            "DocumentSmall",
            fontName=_FONT_REGULAR,
            fontSize=8,
            leading=10,
        ),
        "bold": ParagraphStyle(
            "DocumentBold",
            fontName=_FONT_BOLD,
            fontSize=9,
            leading=12,
        ),
        "right": ParagraphStyle(
            "DocumentRight",
            fontName=_FONT_REGULAR,
            fontSize=9,
            leading=12,
            alignment=TA_RIGHT,
        ),
        "right_bold": ParagraphStyle(
            "DocumentRightBold",
            fontName=_FONT_BOLD,
            fontSize=10,
            leading=13,
            alignment=TA_RIGHT,
        ),
        "recommendation": ParagraphStyle(
            "Recommendation",
            fontName=_FONT_REGULAR,
            fontSize=9,
            leading=13,
        ),
        "signature_note": ParagraphStyle(
            "SignatureNote",
            fontName=_FONT_REGULAR,
            fontSize=7,
            leading=9,
            alignment=TA_CENTER,
        ),
    }


def _p(
    value,
    style: ParagraphStyle,
) -> Paragraph:
    text = "" if value is None else str(value)

    return Paragraph(
        escape(text),
        style,
    )


def _table_style() -> TableStyle:
    return TableStyle(
        [
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                _FONT_BOLD,
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                _FONT_REGULAR,
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.black,
            ),
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.whitesmoke,
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                3,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                3,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                3,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                3,
            ),
        ]
    )


def _numbered_canvas_maker(
    document_label: str,
):
    class NumberedCanvas(Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            page_count = len(self._saved_page_states)

            for page_state in self._saved_page_states:
                self.__dict__.update(page_state)

                self._draw_footer(page_count)

                Canvas.showPage(self)

            Canvas.save(self)

        def _draw_footer(
            self,
            page_count: int,
        ):
            ensure_pdf_fonts()

            self.saveState()

            self.setStrokeColor(colors.lightgrey)
            self.setLineWidth(0.4)

            self.line(
                15 * mm,
                11 * mm,
                A4[0] - 15 * mm,
                11 * mm,
            )

            self.setFont(
                _FONT_REGULAR,
                7,
            )

            self.drawString(
                15 * mm,
                6.5 * mm,
                COMPANY_NAME,
            )

            self.drawCentredString(
                A4[0] / 2,
                6.5 * mm,
                document_label,
            )

            page_text = (
                "\u0421\u0442\u0440\u0430\u043d\u0438\u0446\u0430 "
                f"{self._pageNumber} "
                "\u0438\u0437 "
                f"{page_count}"
            )

            self.drawRightString(
                A4[0] - 15 * mm,
                6.5 * mm,
                page_text,
            )

            self.restoreState()

    return NumberedCanvas


def _document_header(
    title: str,
    document_date: str,
    styles,
):
    return [
        _p(
            COMPANY_NAME,
            styles["company"],
        ),
        HRFlowable(
            width="100%",
            thickness=0.7,
            color=colors.grey,
            spaceBefore=0,
            spaceAfter=4 * mm,
        ),
        _p(
            title,
            styles["title"],
        ),
        _p(
            (f"\u043e\u0442 {document_date}"),
            styles["document_date"],
        ),
    ]


def _client_vehicle_block(
    data: WorkOrderDocumentData,
    styles,
):
    phone = data.client.phone_primary

    if data.client.phone_secondary:
        phone = f"{phone}, {data.client.phone_secondary}"

    vin = data.vehicle.vin or "\u2014"

    year = str(data.vehicle.year) if data.vehicle.year is not None else "\u2014"

    mileage = str(data.vehicle.mileage) if data.vehicle.mileage is not None else "\u2014"

    rows = [
        [
            _p(
                "\u041a\u043b\u0438\u0435\u043d\u0442",
                styles["bold"],
            ),
            _p(
                data.client.full_name,
                styles["normal"],
            ),
            _p(
                "\u0422\u0435\u043b\u0435\u0444\u043e\u043d",
                styles["bold"],
            ),
            _p(
                phone,
                styles["normal"],
            ),
        ],
        [
            _p(
                "\u0410\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044c",
                styles["bold"],
            ),
            _p(
                f"{data.vehicle.brand} {data.vehicle.model}",
                styles["normal"],
            ),
            _p(
                "\u0413\u043e\u0441\u043d\u043e\u043c\u0435\u0440",
                styles["bold"],
            ),
            _p(
                data.vehicle.license_plate,
                styles["normal"],
            ),
        ],
        [
            _p(
                "VIN",
                styles["bold"],
            ),
            _p(
                vin,
                styles["normal"],
            ),
            _p(
                "\u0413\u043e\u0434",
                styles["bold"],
            ),
            _p(
                year,
                styles["normal"],
            ),
        ],
        [
            _p(
                "\u041f\u0440\u043e\u0431\u0435\u0433",
                styles["bold"],
            ),
            _p(
                mileage,
                styles["normal"],
            ),
            "",
            "",
        ],
    ]

    table = Table(
        rows,
        colWidths=[
            28 * mm,
            64 * mm,
            25 * mm,
            63 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.whitesmoke,
                ),
                (
                    "BACKGROUND",
                    (2, 0),
                    (2, 2),
                    colors.whitesmoke,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.grey,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.lightgrey,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    return table


def _works_table(
    data: WorkOrderDocumentData,
    styles,
):
    rows = [
        [
            _p("\u2116", styles["bold"]),
            _p(
                "\u0420\u0430\u0431\u043e\u0442\u0430",
                styles["bold"],
            ),
            _p(
                "\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c",
                styles["bold"],
            ),
        ]
    ]

    if data.works:
        for index, item in enumerate(
            data.works,
            start=1,
        ):
            rows.append(
                [
                    str(index),
                    _p(
                        item.name,
                        styles["small"],
                    ),
                    format_money(item.price),
                ]
            )
    else:
        rows.append(
            [
                "",
                _p(
                    (
                        "\u0412\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u043d\u044b\u0435 "
                        "\u0440\u0430\u0431\u043e\u0442\u044b "
                        "\u043d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u044b"
                    ),
                    styles["small"],
                ),
                "",
            ]
        )

    table = Table(
        rows,
        repeatRows=1,
        colWidths=[
            10 * mm,
            130 * mm,
            40 * mm,
        ],
    )

    table.setStyle(_table_style())

    return table


def _parts_table(
    parts: list[DocumentPart],
    styles,
):
    rows = [
        [
            _p(
                "\u2116",
                styles["bold"],
            ),
            _p(
                "\u0417\u0430\u043f\u0447\u0430\u0441\u0442\u044c",
                styles["bold"],
            ),
            _p(
                "\u041a\u043e\u043b.",
                styles["bold"],
            ),
            _p(
                "\u0426\u0435\u043d\u0430",
                styles["bold"],
            ),
            _p(
                "\u0418\u0442\u043e\u0433\u043e",
                styles["bold"],
            ),
        ]
    ]

    if parts:
        for index, item in enumerate(
            parts,
            start=1,
        ):
            name = escape(item.name)

            if item.supplier:
                name = (
                    f"{name}<br/>"
                    "<font size='7'>"
                    "\u041f\u043e\u0441\u0442\u0430\u0432\u0449\u0438\u043a: "
                    f"{escape(item.supplier)}"
                    "</font>"
                )

            rows.append(
                [
                    str(index),
                    Paragraph(
                        name,
                        styles["small"],
                    ),
                    str(item.quantity),
                    format_money(item.unit_price),
                    format_money(item.total_price),
                ]
            )
    else:
        rows.append(
            [
                "",
                _p(
                    (
                        "\u0417\u0430\u043f\u0447\u0430\u0441\u0442\u0438 "
                        "\u043d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u044b"
                    ),
                    styles["small"],
                ),
                "",
                "",
                "",
            ]
        )

    table = Table(
        rows,
        repeatRows=1,
        colWidths=[
            10 * mm,
            98 * mm,
            16 * mm,
            28 * mm,
            28 * mm,
        ],
    )

    table.setStyle(_table_style())

    return table


def _totals_block(
    data: WorkOrderDocumentData,
    styles,
):
    rows = [
        [
            _p(
                "\u0420\u0430\u0431\u043e\u0442\u044b",
                styles["normal"],
            ),
            _p(
                format_money(data.payment.works_total),
                styles["right"],
            ),
        ],
        [
            _p(
                "\u0417\u0430\u043f\u0447\u0430\u0441\u0442\u0438 \u0421\u0422\u041e",
                styles["normal"],
            ),
            _p(
                format_money(data.payment.sto_parts_total),
                styles["right"],
            ),
        ],
        [
            _p(
                "\u0418\u0422\u041e\u0413\u041e",
                styles["bold"],
            ),
            _p(
                format_money(data.payment.repair_total),
                styles["right_bold"],
            ),
        ],
        [
            _p(
                "\u041e\u043f\u043b\u0430\u0447\u0435\u043d\u043e",
                styles["normal"],
            ),
            _p(
                format_money(data.payment.paid_amount),
                styles["right"],
            ),
        ],
        [
            _p(
                "\u0417\u0430\u0434\u043e\u043b\u0436\u0435\u043d\u043d\u043e\u0441\u0442\u044c",
                styles["bold"],
            ),
            _p(
                format_money(data.payment.debt_amount),
                styles["right_bold"],
            ),
        ],
    ]

    table = Table(
        rows,
        colWidths=[
            58 * mm,
            42 * mm,
        ],
        hAlign="RIGHT",
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.grey,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.lightgrey,
                ),
                (
                    "BACKGROUND",
                    (0, 2),
                    (-1, 2),
                    colors.whitesmoke,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
            ]
        )
    )

    return table


def _recommendations_block(
    data: WorkOrderDocumentData,
    styles,
):
    lines = []

    for item in data.recommendations:
        line = f"\u2022 {escape(item.name)}"

        if item.comment:
            line += f" \u2014 {escape(item.comment)}"

        lines.append(line)

    content = "<br/><br/>".join(lines)

    table = Table(
        [
            [
                Paragraph(
                    content,
                    styles["recommendation"],
                )
            ]
        ],
        colWidths=[
            180 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.whitesmoke,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.grey,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    return table


def _signature_block(
    styles,
):
    signature_rows = [
        [
            _p(
                (
                    "\u041f\u0440\u0435\u0434\u0441\u0442\u0430\u0432\u0438\u0442\u0435\u043b\u044c \u0421\u0422\u041e: "
                    "____________________________"
                ),
                styles["normal"],
            ),
            _p(
                ("\u041a\u043b\u0438\u0435\u043d\u0442: ____________________________"),
                styles["normal"],
            ),
        ],
        [
            _p(
                "\u043f\u043e\u0434\u043f\u0438\u0441\u044c",
                styles["signature_note"],
            ),
            _p(
                "\u043f\u043e\u0434\u043f\u0438\u0441\u044c",
                styles["signature_note"],
            ),
        ],
    ]

    table = Table(
        signature_rows,
        colWidths=[
            90 * mm,
            90 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, 0),
                    2,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    0,
                ),
            ]
        )
    )

    return KeepTogether(
        [
            Spacer(
                1,
                10 * mm,
            ),
            table,
        ]
    )


def build_work_order_pdf(
    data: WorkOrderDocumentData,
) -> bytes:
    styles = _styles()

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=13 * mm,
        bottomMargin=18 * mm,
        title=(
            "\u0417\u0430\u043a\u0430\u0437-\u043d\u0430\u0440\u044f\u0434 "
            f"\u2116{data.work_order_number}"
        ),
    )

    sto_parts = [part for part in data.parts if part.provided_by == "\u0421\u0422\u041e"]

    client_parts = [
        part for part in data.parts if part.provided_by == "\u041a\u043b\u0438\u0435\u043d\u0442"
    ]

    title = (
        "\u0417\u0410\u041a\u0410\u0417-\u041d\u0410\u0420\u042f\u0414 "
        f"\u2116{data.work_order_number}"
    )

    story = []

    story.extend(
        _document_header(
            title,
            data.document_date,
            styles,
        )
    )

    story.extend(
        [
            _client_vehicle_block(
                data,
                styles,
            ),
            _p(
                "\u041f\u0440\u0438\u0447\u0438\u043d\u0430 "
                "\u043e\u0431\u0440\u0430\u0449\u0435\u043d\u0438\u044f",
                styles["heading"],
            ),
            _p(
                data.reason,
                styles["normal"],
            ),
            _p(
                "\u041f\u0435\u0440\u0435\u0447\u0435\u043d\u044c "
                "\u0440\u0430\u0431\u043e\u0442\u044b",
                styles["heading"],
            ),
            _works_table(
                data,
                styles,
            ),
        ]
    )

    if sto_parts:
        story.extend(
            [
                _p(
                    "\u0417\u0430\u043f\u0447\u0430\u0441\u0442\u0438 \u0421\u0422\u041e",
                    styles["heading"],
                ),
                _parts_table(
                    sto_parts,
                    styles,
                ),
            ]
        )

    if client_parts:
        story.extend(
            [
                _p(
                    "\u0417\u0430\u043f\u0447\u0430\u0441\u0442\u0438 "
                    "\u043a\u043b\u0438\u0435\u043d\u0442\u0430",
                    styles["heading"],
                ),
                _parts_table(
                    client_parts,
                    styles,
                ),
            ]
        )

    if not sto_parts and not client_parts:
        story.extend(
            [
                _p(
                    "\u0417\u0430\u043f\u0447\u0430\u0441\u0442\u0438",
                    styles["heading"],
                ),
                _parts_table(
                    [],
                    styles,
                ),
            ]
        )

    if data.recommendations:
        story.extend(
            [
                _p(
                    "\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0438 "
                    "\u043c\u0430\u0441\u0442\u0435\u0440\u0430",
                    styles["heading"],
                ),
                _recommendations_block(
                    data,
                    styles,
                ),
            ]
        )

    story.extend(
        [
            _p(
                "\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u0438 \u043e\u043f\u043b\u0430\u0442\u0430",
                styles["heading"],
            ),
            _totals_block(
                data,
                styles,
            ),
            _signature_block(
                styles,
            ),
        ]
    )

    document_label = (
        "\u0417\u0430\u043a\u0430\u0437-\u043d\u0430\u0440\u044f\u0434 "
        f"\u2116{data.work_order_number}"
    )

    doc.build(
        story,
        canvasmaker=_numbered_canvas_maker(document_label),
    )

    return buffer.getvalue()


def build_completion_act_pdf(
    data: WorkOrderDocumentData,
) -> bytes:
    styles = _styles()

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=13 * mm,
        bottomMargin=18 * mm,
        title=(
            "\u0410\u043a\u0442 "
            "\u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u043d\u044b\u0445 "
            "\u0440\u0430\u0431\u043e\u0442 "
            f"\u2116{data.work_order_number}"
        ),
    )

    sto_parts = [part for part in data.parts if part.provided_by == "\u0421\u0422\u041e"]

    title = (
        "\u0410\u041a\u0422 "
        "\u0412\u042b\u041f\u041e\u041b\u041d\u0415\u041d\u041d\u042b\u0425 "
        "\u0420\u0410\u0411\u041e\u0422 "
        f"\u2116{data.work_order_number}"
    )

    story = []

    story.extend(
        _document_header(
            title,
            data.document_date,
            styles,
        )
    )

    story.extend(
        [
            _client_vehicle_block(
                data,
                styles,
            ),
            _p(
                "\u0412\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u043d\u044b\u0435 "
                "\u0440\u0430\u0431\u043e\u0442\u044b",
                styles["heading"],
            ),
            _works_table(
                data,
                styles,
            ),
            _p(
                "\u0417\u0430\u043f\u0447\u0430\u0441\u0442\u0438 \u0421\u0422\u041e",
                styles["heading"],
            ),
            _parts_table(
                sto_parts,
                styles,
            ),
            _p(
                "\u0418\u0442\u043e\u0433\u0438 \u0438 \u043e\u043f\u043b\u0430\u0442\u0430",
                styles["heading"],
            ),
            _totals_block(
                data,
                styles,
            ),
            _signature_block(
                styles,
            ),
        ]
    )

    document_label = (
        "\u0410\u043a\u0442 "
        "\u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u043d\u044b\u0445 "
        "\u0440\u0430\u0431\u043e\u0442 "
        f"\u2116{data.work_order_number}"
    )

    doc.build(
        story,
        canvasmaker=_numbered_canvas_maker(document_label),
    )

    return buffer.getvalue()
