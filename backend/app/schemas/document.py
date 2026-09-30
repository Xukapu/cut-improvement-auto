from decimal import Decimal

from pydantic import BaseModel


class DocumentClient(BaseModel):
    client_number: int
    full_name: str
    phone_primary: str
    phone_secondary: str | None


class DocumentVehicle(BaseModel):
    vehicle_number: int
    brand: str
    model: str
    license_plate: str
    vin: str | None
    year: int | None
    mileage: int | None


class DocumentWork(BaseModel):
    work_item_number: int
    name: str
    price: Decimal


class DocumentPart(BaseModel):
    part_number: int
    name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    supplier: str | None
    provided_by: str


class DocumentRecommendation(BaseModel):
    recommended_work_number: int
    name: str
    comment: str | None


class DocumentPayment(BaseModel):
    works_total: Decimal
    sto_parts_total: Decimal
    repair_total: Decimal
    paid_amount: Decimal
    debt_amount: Decimal


class WorkOrderDocumentData(BaseModel):
    work_order_number: int
    document_date: str
    status: str
    reason: str

    client: DocumentClient
    vehicle: DocumentVehicle

    works: list[DocumentWork]
    parts: list[DocumentPart]
    recommendations: list[DocumentRecommendation]

    payment: DocumentPayment
