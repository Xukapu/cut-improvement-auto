from collections import defaultdict
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException, status
from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session, aliased

from app.models.appointment import Appointment
from app.models.client import Client
from app.models.employee import Employee
from app.models.part import Part
from app.models.payment import Payment
from app.models.vehicle import Vehicle
from app.models.work_item import (
    WorkItem,
    WorkItemAssignment,
)
from app.models.work_order import WorkOrder
from app.schemas.report import (
    ClientReportResponse,
    ClientSourceItem,
    DashboardAppointmentItem,
    DashboardDebtItem,
    DashboardResponse,
    DashboardWorkOrderItem,
    EmployeeAccrualItem,
    EmployeeAccrualReportResponse,
    EmployeeWorkAccrual,
    FinanceReportResponse,
    NewClientItem,
    ReferralItem,
    RegularClientItem,
    WorkReportItem,
    WorkReportResponse,
)
from app.services.payment import (
    calculate_paid_amount,
    calculate_repair_total,
)

_MONEY = Decimal("0.01")
_HUNDRED = Decimal("100")


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


def normalize_period(
    date_from: date | None,
    date_to: date | None,
) -> tuple[date, date]:
    today = date.today()

    if date_from is None and date_to is None:
        return today, today

    if date_from is None:
        date_from = date_to

    if date_to is None:
        date_to = date_from

    if date_from is None or date_to is None:
        raise RuntimeError("Не удалось определить период отчёта.")

    if date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("Дата начала периода не может быть позже даты окончания периода."),
        )

    return date_from, date_to


def calculate_employee_amount(
    *,
    work_price: Decimal,
    share_percent: Decimal,
    rate_percent: Decimal,
) -> tuple[Decimal, Decimal]:
    share_base = money(work_price * share_percent / _HUNDRED)

    earning = money(share_base * rate_percent / _HUNDRED)

    return share_base, earning


def vehicle_name(
    vehicle: Vehicle,
) -> str:
    return (f"{vehicle.brand} {vehicle.model}").strip()


def get_dashboard(
    db: Session,
    *,
    report_date: date | None,
) -> DashboardResponse:
    selected_date = report_date or date.today()

    appointment_rows = db.execute(
        select(
            Appointment,
            Client,
            Vehicle,
        )
        .join(
            Client,
            Client.id == Appointment.client_id,
        )
        .join(
            Vehicle,
            Vehicle.id == Appointment.vehicle_id,
        )
        .where(
            Appointment.deleted_at.is_(None),
            Client.deleted_at.is_(None),
            Vehicle.deleted_at.is_(None),
            Appointment.appointment_date == selected_date,
        )
        .order_by(
            Appointment.appointment_time.asc(),
        )
    ).all()

    appointments = [
        DashboardAppointmentItem(
            appointment_number=appointment.appointment_number,
            appointment_time=appointment.appointment_time,
            client_number=client.client_number,
            client_name=client.full_name,
            vehicle_number=vehicle.vehicle_number,
            vehicle_name=vehicle_name(vehicle),
            license_plate=vehicle.license_plate,
            reason=appointment.reason,
            status=appointment.status.value,
        )
        for appointment, client, vehicle in appointment_rows
    ]

    work_order_rows = db.execute(
        select(
            WorkOrder,
            Client,
            Vehicle,
        )
        .join(
            Client,
            Client.id == WorkOrder.client_id,
        )
        .join(
            Vehicle,
            Vehicle.id == WorkOrder.vehicle_id,
        )
        .where(
            WorkOrder.deleted_at.is_(None),
            Client.deleted_at.is_(None),
            Vehicle.deleted_at.is_(None),
            WorkOrder.status.in_(
                [
                    "in_progress",
                    "ready",
                ]
            ),
        )
        .order_by(
            WorkOrder.work_order_number.asc(),
        )
    ).all()

    in_progress = []
    ready = []

    for order, client, vehicle in work_order_rows:
        item = DashboardWorkOrderItem(
            work_order_number=order.work_order_number,
            client_number=client.client_number,
            client_name=client.full_name,
            vehicle_number=vehicle.vehicle_number,
            vehicle_name=vehicle_name(vehicle),
            license_plate=vehicle.license_plate,
            status=order.status.value,
            reason=order.reason,
        )

        if order.status.value == "in_progress":
            in_progress.append(item)

        elif order.status.value == "ready":
            ready.append(item)

    debt_rows = db.execute(
        select(
            WorkOrder,
            Client,
        )
        .join(
            Client,
            Client.id == WorkOrder.client_id,
        )
        .where(
            WorkOrder.deleted_at.is_(None),
            Client.deleted_at.is_(None),
            WorkOrder.status == "issued",
        )
        .order_by(
            WorkOrder.work_order_number.asc(),
        )
    ).all()

    debts = []
    debt_total = Decimal("0")

    for order, client in debt_rows:
        _, _, repair_total = calculate_repair_total(
            db,
            order.id,
        )

        paid_amount = calculate_paid_amount(
            db,
            order.id,
        )

        debt_amount = money(repair_total - paid_amount)

        if debt_amount <= 0:
            continue

        debt_total += debt_amount

        debts.append(
            DashboardDebtItem(
                work_order_number=(order.work_order_number),
                client_number=client.client_number,
                client_name=client.full_name,
                repair_total=repair_total,
                paid_amount=paid_amount,
                debt_amount=debt_amount,
            )
        )

    scheduled_count = sum(1 for item in appointments if item.status == "scheduled")

    no_show_count = sum(1 for item in appointments if item.status == "no_show")

    return DashboardResponse(
        report_date=selected_date,
        appointments_today=appointments,
        in_progress=in_progress,
        ready=ready,
        debts=debts,
        scheduled_count=scheduled_count,
        no_show_count=no_show_count,
        in_progress_count=len(in_progress),
        ready_count=len(ready),
        debt_total=money(debt_total),
    )


def get_client_report(
    db: Session,
    *,
    date_from: date | None,
    date_to: date | None,
) -> ClientReportResponse:
    start_date, end_date = normalize_period(
        date_from,
        date_to,
    )

    new_clients = list(
        db.scalars(
            select(Client)
            .where(
                Client.deleted_at.is_(None),
                cast(
                    Client.created_at,
                    Date,
                ).between(
                    start_date,
                    end_date,
                ),
            )
            .order_by(
                Client.client_number.asc(),
            )
        ).all()
    )

    visits = (
        select(
            WorkOrder.client_id.label("client_id"),
            func.count(WorkOrder.id).label("visits"),
        )
        .where(
            WorkOrder.deleted_at.is_(None),
            WorkOrder.status == "issued",
        )
        .group_by(WorkOrder.client_id)
        .subquery()
    )

    regular_rows = db.execute(
        select(
            Client,
            visits.c.visits,
        )
        .join(
            visits,
            visits.c.client_id == Client.id,
        )
        .where(
            Client.deleted_at.is_(None),
            Client.archived_at.is_(None),
            visits.c.visits >= 4,
        )
        .order_by(
            visits.c.visits.desc(),
            Client.client_number.asc(),
        )
    ).all()

    source_rows = db.execute(
        select(
            Client.source,
            func.count(Client.id),
        )
        .where(
            Client.deleted_at.is_(None),
            cast(
                Client.created_at,
                Date,
            ).between(
                start_date,
                end_date,
            ),
        )
        .group_by(Client.source)
        .order_by(
            Client.source.asc(),
        )
    ).all()

    Referrer = aliased(Client)

    referral_rows = db.execute(
        select(
            Client,
            Referrer,
        )
        .join(
            Referrer,
            Referrer.id == Client.referred_by_client_id,
        )
        .where(
            Client.deleted_at.is_(None),
            Client.referred_by_client_id.is_not(None),
            cast(
                Client.created_at,
                Date,
            ).between(
                start_date,
                end_date,
            ),
        )
        .order_by(
            Client.client_number.asc(),
        )
    ).all()

    return ClientReportResponse(
        date_from=start_date,
        date_to=end_date,
        new_clients_count=len(new_clients),
        regular_clients_count=len(regular_rows),
        new_clients=[
            NewClientItem(
                client_number=client.client_number,
                full_name=client.full_name,
                source=client.source.value,
                created_at=client.created_at,
            )
            for client in new_clients
        ],
        regular_clients=[
            RegularClientItem(
                client_number=client.client_number,
                full_name=client.full_name,
                visits=int(visits_count),
            )
            for client, visits_count in regular_rows
        ],
        sources=[
            ClientSourceItem(
                source=source.value,
                count=int(count),
            )
            for source, count in source_rows
        ],
        referrals=[
            ReferralItem(
                client_number=client.client_number,
                client_name=client.full_name,
                referred_by_client_number=(referrer.client_number),
                referred_by_name=(referrer.full_name),
            )
            for client, referrer in referral_rows
        ],
    )


def get_finance_report(
    db: Session,
    *,
    date_from: date | None,
    date_to: date | None,
) -> FinanceReportResponse:
    start_date, end_date = normalize_period(
        date_from,
        date_to,
    )

    payment_rows = db.execute(
        select(
            Payment.method,
            func.coalesce(
                func.sum(Payment.amount),
                0,
            ),
        )
        .where(
            Payment.deleted_at.is_(None),
            cast(
                Payment.paid_at,
                Date,
            ).between(
                start_date,
                end_date,
            ),
        )
        .group_by(Payment.method)
    ).all()

    by_method = {
        "cash": Decimal("0"),
        "card": Decimal("0"),
        "transfer": Decimal("0"),
    }

    for method, amount in payment_rows:
        by_method[method.value] = money(amount)

    payments_received = money(
        sum(
            by_method.values(),
            Decimal("0"),
        )
    )

    works_total = money(
        db.scalar(
            select(
                func.coalesce(
                    func.sum(WorkItem.price),
                    0,
                )
            ).where(
                WorkItem.deleted_at.is_(None),
                cast(
                    WorkItem.created_at,
                    Date,
                ).between(
                    start_date,
                    end_date,
                ),
            )
        )
    )

    sto_parts_total = money(
        db.scalar(
            select(
                func.coalesce(
                    func.sum(Part.unit_price * Part.quantity),
                    0,
                )
            ).where(
                Part.deleted_at.is_(None),
                Part.provided_by == "sto",
                cast(
                    Part.created_at,
                    Date,
                ).between(
                    start_date,
                    end_date,
                ),
            )
        )
    )

    issued_orders = list(
        db.scalars(
            select(WorkOrder).where(
                WorkOrder.deleted_at.is_(None),
                WorkOrder.status == "issued",
            )
        ).all()
    )

    current_debt = Decimal("0")

    for order in issued_orders:
        _, _, order_total = calculate_repair_total(
            db,
            order.id,
        )

        paid = calculate_paid_amount(
            db,
            order.id,
        )

        debt = money(order_total - paid)

        if debt > 0:
            current_debt += debt

    return FinanceReportResponse(
        date_from=start_date,
        date_to=end_date,
        payments_received=(payments_received),
        cash_received=by_method["cash"],
        card_received=by_method["card"],
        transfer_received=(by_method["transfer"]),
        works_total=works_total,
        sto_parts_total=sto_parts_total,
        repair_total=money(works_total + sto_parts_total),
        current_debt=money(current_debt),
    )


def get_work_report(
    db: Session,
    *,
    date_from: date | None,
    date_to: date | None,
) -> WorkReportResponse:
    start_date, end_date = normalize_period(
        date_from,
        date_to,
    )

    rows = db.execute(
        select(
            WorkItem,
            WorkOrder.work_order_number,
        )
        .join(
            WorkOrder,
            WorkOrder.id == WorkItem.work_order_id,
        )
        .where(
            WorkItem.deleted_at.is_(None),
            WorkOrder.deleted_at.is_(None),
            cast(
                WorkItem.created_at,
                Date,
            ).between(
                start_date,
                end_date,
            ),
        )
        .order_by(
            WorkItem.created_at.asc(),
            WorkItem.work_item_number.asc(),
        )
    ).all()

    items = [
        WorkReportItem(
            work_order_number=(work_order_number),
            work_item_number=(work_item.work_item_number),
            name=work_item.name,
            price=money(work_item.price),
            recorded_at=(work_item.created_at),
        )
        for work_item, work_order_number in rows
    ]

    return WorkReportResponse(
        date_from=start_date,
        date_to=end_date,
        total=len(items),
        total_amount=money(
            sum(
                (item.price for item in items),
                Decimal("0"),
            )
        ),
        items=items,
    )


def get_employee_accrual_report(
    db: Session,
    *,
    date_from: date | None,
    date_to: date | None,
) -> EmployeeAccrualReportResponse:
    start_date, end_date = normalize_period(
        date_from,
        date_to,
    )

    rows = db.execute(
        select(
            WorkItemAssignment,
            WorkItem,
            Employee,
            WorkOrder.work_order_number,
        )
        .join(
            WorkItem,
            WorkItem.id == WorkItemAssignment.work_item_id,
        )
        .join(
            Employee,
            Employee.id == WorkItemAssignment.employee_id,
        )
        .join(
            WorkOrder,
            WorkOrder.id == WorkItem.work_order_id,
        )
        .where(
            WorkItemAssignment.deleted_at.is_(None),
            WorkItem.deleted_at.is_(None),
            Employee.deleted_at.is_(None),
            WorkOrder.deleted_at.is_(None),
            cast(
                WorkItem.created_at,
                Date,
            ).between(
                start_date,
                end_date,
            ),
        )
        .order_by(
            Employee.employee_number.asc(),
            WorkItem.created_at.asc(),
            WorkItem.work_item_number.asc(),
        )
    ).all()

    grouped: dict[
        int,
        dict,
    ] = defaultdict(
        lambda: {
            "employee_name": "",
            "works": [],
            "share_base": Decimal("0"),
            "earnings": Decimal("0"),
        }
    )

    for (
        assignment,
        work_item,
        employee,
        work_order_number,
    ) in rows:
        share_base, earning = calculate_employee_amount(
            work_price=work_item.price,
            share_percent=(assignment.share_percent),
            rate_percent=(assignment.rate_percent_snapshot),
        )

        employee_data = grouped[employee.employee_number]

        employee_data["employee_name"] = employee.full_name

        employee_data["share_base"] += share_base

        employee_data["earnings"] += earning

        employee_data["works"].append(
            EmployeeWorkAccrual(
                work_order_number=(work_order_number),
                work_item_number=(work_item.work_item_number),
                work_name=work_item.name,
                work_price=money(work_item.price),
                share_percent=money(assignment.share_percent),
                share_base=share_base,
                rate_percent_snapshot=money(assignment.rate_percent_snapshot),
                earning_amount=earning,
                recorded_at=(work_item.created_at),
            )
        )

    employees = []

    for employee_number in sorted(grouped):
        data = grouped[employee_number]

        employees.append(
            EmployeeAccrualItem(
                employee_number=(employee_number),
                employee_name=(data["employee_name"]),
                works=data["works"],
                total_share_base=money(data["share_base"]),
                total_earnings=money(data["earnings"]),
            )
        )

    grand_total = money(
        sum(
            (employee.total_earnings for employee in employees),
            Decimal("0"),
        )
    )

    return EmployeeAccrualReportResponse(
        date_from=start_date,
        date_to=end_date,
        employees=employees,
        grand_total=grand_total,
    )
