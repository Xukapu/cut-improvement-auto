from pydantic import BaseModel, ConfigDict, Field, field_validator


class RecommendedWorkWrite(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=500,
    )

    comment: str | None = Field(
        default=None,
        max_length=2000,
    )

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Название рекомендованной работы не может быть пустым.")

        return value

    @field_validator("comment")
    @classmethod
    def normalize_comment(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class RecommendedWorkCreate(RecommendedWorkWrite):
    pass


class RecommendedWorkUpdate(RecommendedWorkWrite):
    pass


class RecommendedWorkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommended_work_number: int
    name: str
    comment: str | None


class RecommendedWorkListResponse(BaseModel):
    items: list[RecommendedWorkResponse]
    total: int
