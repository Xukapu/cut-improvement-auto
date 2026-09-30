from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel


class DashboardAppointmentItem(BaseModel):
    appointment_number: int
    appointment_time: time

    client_number: int
    client_name: str

    vehicle_number: int
    vehicle_name: str
    license_plate: str

    reason: str
    status: str


class DashboardWorkOrderItem(BaseModel):
    work_order_number: int

    client_number: int
    client_name: str

    vehicle_number: int
    vehicle_name: str
    license_plate: str

    status: str
    reason: str


class DashboardDebtItem(BaseModel):
    work_order_number: int

    client_number: int
    client_name: str

    repair_total: Decimal
    paid_amount: Decimal
    debt_amount: Decimal


class DashboardResponse(BaseModel):
    report_date: date

    appointments_today: list[DashboardAppointmentItem]
    in_progress: list[DashboardWorkOrderItem]
    ready: list[DashboardWorkOrderItem]
    debts: list[DashboardDebtItem]

    scheduled_count: int
    no_show_count: int
    in_progress_count: int
    ready_count: int

    debt_total: Decimal


class NewClientItem(BaseModel):
    client_number: int
    full_name: str
    source: str
    created_at: datetime


class RegularClientItem(BaseModel):
    client_number: int
    full_name: str
    visits: int


class ClientSourceItem(BaseModel):
    source: str
    count: int


class ReferralItem(BaseModel):
    client_number: int
    client_name: str

    referred_by_client_number: int
    referred_by_name: str


class ClientReportResponse(BaseModel):
    date_from: date
    date_to: date

    new_clients_count: int
    regular_clients_count: int

    new_clients: list[NewClientItem]
    regular_clients: list[RegularClientItem]

    sources: list[ClientSourceItem]
    referrals: list[ReferralItem]


class FinanceReportResponse(BaseModel):
    date_from: date
    date_to: date

    payments_received: Decimal

    cash_received: Decimal
    card_received: Decimal
    transfer_received: Decimal

    works_total: Decimal
    sto_parts_total: Decimal
    repair_total: Decimal

    current_debt: Decimal


class WorkReportItem(BaseModel):
    work_order_number: int
    work_item_number: int

    name: str
    price: Decimal

    recorded_at: datetime


class WorkReportResponse(BaseModel):
    date_from: date
    date_to: date

    total: int
    total_amount: Decimal

    items: list[WorkReportItem]


class EmployeeWorkAccrual(BaseModel):
    work_order_number: int
    work_item_number: int
    work_name: str

    work_price: Decimal

    share_percent: Decimal
    share_base: Decimal

    rate_percent_snapshot: Decimal
    earning_amount: Decimal

    recorded_at: datetime


class EmployeeAccrualItem(BaseModel):
    employee_number: int
    employee_name: str

    works: list[EmployeeWorkAccrual]

    total_share_base: Decimal
    total_earnings: Decimal


class EmployeeAccrualReportResponse(BaseModel):
    date_from: date
    date_to: date

    employees: list[EmployeeAccrualItem]

    grand_total: Decimal
