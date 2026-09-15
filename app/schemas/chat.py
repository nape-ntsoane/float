from typing import Any

from pydantic import BaseModel


# command_type is a plain str, not the CommandType enum - an unrecognised
# value must reach the handler and get a menu back, not a 422 from pydantic
class InboundMessage(BaseModel):
    command_type: str
    payload: dict[str, Any] = {}


class OutboundMessage(BaseModel):
    message: str
    options: list[str] = []
