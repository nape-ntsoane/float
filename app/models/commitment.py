from datetime import datetime

from pydantic import BaseModel

from app.models.enums import CommitmentStatus, CommitmentType


# a customer's own declared spending intention, tracked against real transactions
class Commitment(BaseModel):
    id: str
    type: CommitmentType
    scope: str  # a category name, or "general" for an account-wide commitment
    target_value: float | None = None  # required for cap/earmark, unused for abstain
    window_start: datetime
    window_end: datetime
    status: CommitmentStatus = CommitmentStatus.active
    created_at: datetime
    resolved_at: datetime | None = None
    cumulative_in_scope_spend: float = 0.0  # only meaningful for cap
