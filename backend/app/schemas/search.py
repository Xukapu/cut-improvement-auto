from pydantic import BaseModel

from app.models.client import ClientSource


class SearchClientResult(BaseModel):
    client_number: int
    full_name: str

    phone_primary: str
    phone_secondary: str | None

    source: ClientSource
    internal_mark: bool


class SearchVehicleResult(BaseModel):
    vehicle_number: int

    license_plate: str
    vin: str | None

    brand: str
    model: str

    year: int | None
    mileage: int | None

    current_owner_client_number: int
    current_owner_name: str


class GlobalSearchResponse(BaseModel):
    query: str

    clients: list[SearchClientResult]
    vehicles: list[SearchVehicleResult]

    total_clients: int
    total_vehicles: int
    total: int
