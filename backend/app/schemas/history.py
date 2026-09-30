from datetime import date, time

from pydantic import BaseModel

from app.models.appointment import AppointmentStatus
from app.models.client import ClientSource


class ClientHistoryVehicle(BaseModel):
    vehicle_number: int
    license_plate: str
    vin: str | None
    brand: str
    model: str
    year: int | None
    mileage: int | None

    is_current_owner: bool
    ownership_started_at: date
    ownership_ended_at: date | None


class ClientHistoryAppointment(BaseModel):
    appointment_number: int

    vehicle_number: int
    license_plate: str

    appointment_date: date
    appointment_time: time

    reason: str
    comment: str | None

    status: AppointmentStatus


class ClientHistoryResponse(BaseModel):
    client_number: int
    full_name: str

    phone_primary: str
    phone_secondary: str | None

    source: ClientSource

    referred_by_client_number: int | None
    referred_by_client_name: str | None

    internal_mark: bool
    notes: str | None

    is_archived: bool

    vehicles: list[ClientHistoryVehicle]
    appointments: list[ClientHistoryAppointment]


class VehicleHistoryOwner(BaseModel):
    client_number: int
    client_name: str

    is_current: bool
    started_at: date
    ended_at: date | None


class VehicleHistoryAppointment(BaseModel):
    appointment_number: int

    client_number: int
    client_name: str

    appointment_date: date
    appointment_time: time

    reason: str
    comment: str | None

    status: AppointmentStatus


class VehicleHistoryResponse(BaseModel):
    vehicle_number: int

    license_plate: str
    vin: str | None

    brand: str
    model: str
    year: int | None
    mileage: int | None

    owners: list[VehicleHistoryOwner]
    appointments: list[VehicleHistoryAppointment]
