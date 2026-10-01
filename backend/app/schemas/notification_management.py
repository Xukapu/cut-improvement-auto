from datetime import datetime

from pydantic import BaseModel, Field


class CustomerNotificationUpdate(BaseModel):
    message_text: str = Field(
        min_length=1,
        max_length=2000,
    )

    scheduled_for: datetime
