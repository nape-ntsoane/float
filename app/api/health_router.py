from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_health_service
from app.models.health import HealthResponse
from app.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health(service: Annotated[HealthService, Depends(get_health_service)]) -> HealthResponse:
    return service.check()
