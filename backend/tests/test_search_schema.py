from app.models.client import ClientSource
from app.schemas.search import (
    GlobalSearchResponse,
    SearchClientResult,
    SearchVehicleResult,
)


def test_global_search_response() -> None:
    result = GlobalSearchResponse(
        query="Volkswagen",
        clients=[
            SearchClientResult(
                client_number=2,
                full_name="Иван Иванов",
                phone_primary="+79990000000",
                phone_secondary=None,
                source=ClientSource.OTHER,
                internal_mark=False,
            )
        ],
        vehicles=[
            SearchVehicleResult(
                vehicle_number=1,
                license_plate="А123ВС77",
                vin="XW8ZZZ61ZKG000001",
                brand="Volkswagen",
                model="Polo",
                year=2020,
                mileage=55000,
                current_owner_client_number=2,
                current_owner_name="Иван Иванов",
            )
        ],
        total_clients=1,
        total_vehicles=1,
        total=2,
    )

    assert result.total == 2
    assert result.clients[0].client_number == 2
    assert result.vehicles[0].vehicle_number == 1


def test_search_can_return_only_clients() -> None:
    result = GlobalSearchResponse(
        query="Иван",
        clients=[
            SearchClientResult(
                client_number=2,
                full_name="Иван Иванов",
                phone_primary="+79990000000",
                phone_secondary=None,
                source=ClientSource.OTHER,
                internal_mark=False,
            )
        ],
        vehicles=[],
        total_clients=1,
        total_vehicles=0,
        total=1,
    )

    assert result.total_clients == 1
    assert result.total_vehicles == 0
