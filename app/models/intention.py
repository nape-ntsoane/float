from pydantic import BaseModel

from app.models.enums import IntentionVerdict


# the outcome of checking one hypothetical purchase against the current position
class IntentionResult(BaseModel):
    verdict: IntentionVerdict
    provisional_free: float
    provisional_close: float
    days_until_affordable: float | None = None  # only set when not_affordable
