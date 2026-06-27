from fastapi import APIRouter, Depends

from app.dependencies import get_services
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.schemas.ledger import LedgerEntryResponse

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(data: CustomerCreate, services: dict = Depends(get_services)):
    return services["customer"].create_customer(data)


@router.get("", response_model=list[CustomerResponse])
def list_customers(services: dict = Depends(get_services)):
    return services["customer"].list_customers()


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, services: dict = Depends(get_services)):
    return services["customer"].get_customer(customer_id)


@router.get("/{customer_id}/ledger", response_model=list[LedgerEntryResponse])
def get_customer_ledger(customer_id: int, services: dict = Depends(get_services)):
    """Return append-only ledger history for one customer."""
    services["customer"].get_customer(customer_id)
    return services["ledger"].get_customer_ledger(customer_id)
