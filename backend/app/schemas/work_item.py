from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator


class WorkAssignmentInput(BaseModel):
    employee_number: int = Field(ge=1)

    share_percent: Decimal = Field(
        gt=0,
        le=100,
        decimal_places=2,
    )


class WorkItemWrite(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=500,
    )

    price: Decimal = Field(
        ge=0,
        decimal_places=2,
    )

    assignments: list[WorkAssignmentInput] = Field(
        min_length=1,
    )

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Название работы не может быть пустым.")

        return value

    @model_validator(mode="after")
    def validate_assignments(self):
        employee_numbers = [item.employee_number for item in self.assignments]

        if len(employee_numbers) != len(set(employee_numbers)):
            raise ValueError("Один сотрудник не может быть указан в одной работе дважды.")

        total = sum(
            (item.share_percent for item in self.assignments),
            Decimal("0"),
        )

        if total != Decimal("100"):
            raise ValueError("Сумма долей исполнителей должна быть ровно 100%.")

        return self


class WorkItemCreate(WorkItemWrite):
    pass


class WorkItemUpdate(WorkItemWrite):
    pass


class WorkAssignmentPublicResponse(BaseModel):
    employee_number: int
    employee_name: str


class WorkItemPublicResponse(BaseModel):
    work_item_number: int
    name: str
    price: Decimal

    assignments: list[WorkAssignmentPublicResponse]


class WorkAssignmentFinancialResponse(WorkAssignmentPublicResponse):
    share_percent: Decimal
    rate_percent_snapshot: Decimal
    earning_amount: Decimal


class WorkItemFinancialResponse(BaseModel):
    work_item_number: int

    name: str
    price: Decimal

    assignments: list[WorkAssignmentFinancialResponse]

    total_employee_earnings: Decimal


class WorkItemListResponse(BaseModel):
    items: list[WorkItemPublicResponse]
    total: int


class WorkItemFinancialListResponse(BaseModel):
    items: list[WorkItemFinancialResponse]
    total: int
