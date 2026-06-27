from fastapi import APIRouter, Depends

from app.dependencies import get_services
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("", response_model=PlanResponse, status_code=201)
def create_plan(data: PlanCreate, services: dict = Depends(get_services)):
    return services["plan"].create_plan(data)


@router.get("", response_model=list[PlanResponse])
def list_plans(services: dict = Depends(get_services)):
    return services["plan"].list_plans()


@router.patch("/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: int, data: PlanUpdate, services: dict = Depends(get_services)):
    """Update plan details or deactivate by sending {\"is_active\": false}."""
    return services["plan"].update_plan(plan_id, data)
