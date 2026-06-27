from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class LedgerEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    invoice_id: int
    entry_type: str
    amount: Decimal
    currency: str
    reference_id: int
    description: str | None = None
    created_at: datetime
