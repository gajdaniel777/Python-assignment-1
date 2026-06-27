from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PlanCreate(BaseModel):
    name: str
    description: str | None = None
    billing_cycle: str = "monthly"
    price: Decimal = Field(gt=0)
    currency: str = "USD"
    notes: str | None = None


class PlanUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    billing_cycle: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    currency: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    billing_cycle: str
    price: Decimal
    currency: str
    notes: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
