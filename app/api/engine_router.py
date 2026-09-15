from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_event_loop
from app.engine.event_loop import EventLoop
from app.models.notification import Notification
from app.schemas.simulate import SimulateRequest

router = APIRouter(prefix="/engine", tags=["engine"])


@router.post("/run", response_model=list[Notification])
def run(event_loop: Annotated[EventLoop, Depends(get_event_loop)]) -> list[Notification]:
    return event_loop.run()


@router.post("/simulate", response_model=list[Notification])
def simulate(
    request: SimulateRequest,
    event_loop: Annotated[EventLoop, Depends(get_event_loop)],
) -> list[Notification]:
    return event_loop.simulate(request.amount, request.category_id, request.narrative)
