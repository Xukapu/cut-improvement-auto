import pytest
from app.schemas.vehicle import (
    TransferVehicleRequest,
    VehicleCreate,
)
from pydantic import ValidationError


def test_vehicle_fields_are_normalized() -> None:
    vehicle = VehicleCreate(
        owner_client_number=1,
        license_plate=" а123вс 77 ",
        vin="xw8zzz61zkg000001",
        brand="  Volkswagen ",
        model=" Polo ",
        year=2020,
        mileage=50000,
    )

    assert vehicle.license_plate == "А123ВС77"
    assert vehicle.vin == "XW8ZZZ61ZKG000001"
    assert vehicle.brand == "Volkswagen"
    assert vehicle.model == "Polo"


def test_invalid_vin_is_rejected() -> None:
    with pytest.raises(ValidationError):
        VehicleCreate(
            owner_client_number=1,
            license_plate="А123ВС77",
            vin="INVALIDVIN",
            brand="Volkswagen",
            model="Polo",
        )


def test_negative_mileage_is_rejected() -> None:
    with pytest.raises(ValidationError):
        VehicleCreate(
            owner_client_number=1,
            license_plate="А123ВС77",
            brand="Volkswagen",
            model="Polo",
            mileage=-1,
        )


def test_owner_number_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        VehicleCreate(
            owner_client_number=0,
            license_plate="А123ВС77",
            brand="Volkswagen",
            model="Polo",
        )


def test_transfer_owner_number_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        TransferVehicleRequest(
            new_owner_client_number=0,
        )
