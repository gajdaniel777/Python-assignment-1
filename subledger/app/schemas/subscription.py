from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubscriptionCreate(BaseModel):
    customer_id: int
    plan_id: int


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    plan_id: int
    status: str
    start_date: datetime
    current_period_start: datetime
    current_period_end: datetime
    cancelled_at: datetime | None = None
    created_at: datetime
