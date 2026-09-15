from datetime import datetime

from pydantic import BaseModel

from app.models.enums import Severity


# what a rule produces when it has something to say - the customer-facing output of the whole engine
class Notification(BaseModel):
    severity: Severity
    triggering_rule: str
    triggering_event: str  # the transaction id that caused this, not the transaction itself
    timestamp: datetime
    message: str
