from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_interaction_handler
from app.engine.interaction_handler import InteractionHandler
from app.schemas.chat import InboundMessage, OutboundMessage

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=OutboundMessage)
def message(
    inbound: InboundMessage,
    handler: Annotated[InteractionHandler, Depends(get_interaction_handler)],
) -> OutboundMessage:
    return handler.handle(inbound)
