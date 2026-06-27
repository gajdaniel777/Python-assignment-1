from fastapi import APIRouter, Depends

from app.dependencies import get_services
from app.schemas.payment import PaymentCreate, PaymentRecordResponse, PaymentAttemptResponse

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/record", response_model=PaymentRecordResponse, status_code=201)
def record_payment(data: PaymentCreate, services: dict = Depends(get_services)):
    payment, invoice = services["payment"].record_payment(data)
    return PaymentRecordResponse(
        payment_attempt=PaymentAttemptResponse.model_validate(payment),
        invoice_status=invoice.status,
        amount_paid=invoice.amount_paid,
    )
