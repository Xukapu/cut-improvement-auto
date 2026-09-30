from datetime import date, time

from app.models.appointment import AppointmentStatus
from app.models.client import ClientSource
from app.schemas.history import (
    ClientHistoryAppointment,
    ClientHistoryResponse,
    ClientHistoryVehicle,
    VehicleHistoryAppointment,
    VehicleHistoryOwner,
    VehicleHistoryResponse,
)


def test_client_history_schema() -> None:
    result = ClientHistoryResponse(
        client_number=2,
        full_name="Иван Иванов",
        phone_primary="+79990000000",
        phone_secondary=None,
        source=ClientSource.OTHER,
        referred_by_client_number=None,
        referred_by_client_name=None,
        internal_mark=False,
        notes=None,
        is_archived=False,
        vehicles=[
            ClientHistoryVehicle(
                vehicle_number=1,
                license_plate="А123ВС77",
                vin=None,
                brand="Volkswagen",
                model="Polo",
                year=2020,
                mileage=55000,
                is_current_owner=True,
                ownership_started_at=date(2026, 9, 30),
                ownership_ended_at=None,
            )
        ],
        appointments=[
            ClientHistoryAppointment(
                appointment_number=1,
                vehicle_number=1,
                license_plate="А123ВС77",
                appointment_date=date(2026, 10, 1),
                appointment_time=time(12, 0),
                reason="Замена масла",
                comment=None,
                status=AppointmentStatus.NO_SHOW,
            )
        ],
    )

    assert result.client_number == 2
    assert len(result.vehicles) == 1
    assert len(result.appointments) == 1


def test_vehicle_history_schema() -> None:
    result = VehicleHistoryResponse(
        vehicle_number=1,
        license_plate="А123ВС77",
        vin=None,
        brand="Volkswagen",
        model="Polo",
        year=2020,
        mileage=55000,
        owners=[
            VehicleHistoryOwner(
                client_number=2,
                client_name="Иван Иванов",
                is_current=True,
                started_at=date(2026, 9, 30),
                ended_at=None,
            )
        ],
        appointments=[
            VehicleHistoryAppointment(
                appointment_number=1,
                client_number=2,
                client_name="Иван Иванов",
                appointment_date=date(2026, 10, 1),
                appointment_time=time(12, 0),
                reason="Замена масла",
                comment=None,
                status=AppointmentStatus.NO_SHOW,
            )
        ],
    )

    assert result.vehicle_number == 1
    assert len(result.owners) == 1
    assert len(result.appointments) == 1
