from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_event_loop
from app.engine.event_loop import EventLoop
from app.models.notification import Notification

router = APIRouter(prefix="/engine", tags=["engine"])


@router.post("/run", response_model=list[Notification])
def run(event_loop: Annotated[EventLoop, Depends(get_event_loop)]) -> list[Notification]:
    return event_loop.run()
