from fastapi import APIRouter, Depends, Query

from app.dependencies import get_services
from app.schemas.invoice import InvoiceGenerateRequest, InvoiceResponse

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/generate", response_model=InvoiceResponse, status_code=201)
def generate_invoice(data: InvoiceGenerateRequest, services: dict = Depends(get_services)):
    return services["invoice"].generate_invoice(data)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, services: dict = Depends(get_services)):
    return services["invoice"].get_invoice(invoice_id)


@router.get("", response_model=list[InvoiceResponse])
def list_invoices(
    subscription_id: int | None = Query(None),
    customer_id: int | None = Query(None),
    services: dict = Depends(get_services),
):
    return services["invoice"].list_invoices(
        subscription_id=subscription_id,
        customer_id=customer_id,
    )
