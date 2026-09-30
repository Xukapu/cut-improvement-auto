import re
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VehicleBase(BaseModel):
    license_plate: str = Field(min_length=1, max_length=32)
    vin: str | None = Field(default=None, max_length=17)
    brand: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int | None = Field(default=None, ge=1886, le=2100)
    mileage: int | None = Field(default=None, ge=0)

    @field_validator("license_plate")
    @classmethod
    def normalize_license_plate(cls, value: str) -> str:
        value = re.sub(r"\s+", "", value.strip().upper())

        if not value:
            raise ValueError("Госномер не может быть пустым.")

        return value

    @field_validator("vin")
    @classmethod
    def normalize_vin(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip().upper()

        if not value:
            return None

        if not re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", value):
            raise ValueError("VIN должен содержать 17 символов и не может содержать I, O или Q.")

        return value

    @field_validator("brand", "model")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Поле не может быть пустым.")

        return value


class VehicleCreate(VehicleBase):
    owner_client_number: int = Field(ge=1)


class VehicleUpdate(VehicleBase):
    pass


class TransferVehicleRequest(BaseModel):
    new_owner_client_number: int = Field(ge=1)


class VehicleResponse(VehicleBase):
    model_config = ConfigDict(from_attributes=True)

    vehicle_number: int
    current_owner_client_number: int
    current_owner_name: str


class VehicleListResponse(BaseModel):
    items: list[VehicleResponse]
    total: int
    limit: int
    offset: int


class VehicleOwnerHistoryItem(BaseModel):
    client_number: int
    client_name: str

    is_current: bool
    started_at: date
    ended_at: date | None


class VehicleOwnerHistoryResponse(BaseModel):
    vehicle_number: int
    owners: list[VehicleOwnerHistoryItem]
