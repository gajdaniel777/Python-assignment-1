from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PaymentStatus


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: Decimal = Field(gt=0)
    currency: str
    status: PaymentStatus
    provider_reference: str
    failure_reason: str | None = None


class PaymentAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    amount: Decimal
    currency: str
    status: str
    provider_reference: str
    failure_reason: str | None
    created_at: datetime


class PaymentRecordResponse(BaseModel):
    payment_attempt: PaymentAttemptResponse
    invoice_status: str
    amount_paid: Decimal
