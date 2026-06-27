from fastapi import APIRouter, Depends

from app.dependencies import get_services
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("", response_model=SubscriptionResponse, status_code=201)
def create_subscription(data: SubscriptionCreate, services: dict = Depends(get_services)):
    return services["subscription"].create_subscription(data.customer_id, data.plan_id)


@router.get("", response_model=list[SubscriptionResponse])
def list_subscriptions(services: dict = Depends(get_services)):
    return services["subscription"].list_subscriptions()


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(subscription_id: int, services: dict = Depends(get_services)):
    return services["subscription"].get_subscription(subscription_id)


@router.patch("/{subscription_id}/cancel", response_model=SubscriptionResponse)
def cancel_subscription(subscription_id: int, services: dict = Depends(get_services)):
    return services["subscription"].cancel_subscription(subscription_id)
