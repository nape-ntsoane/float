from pydantic import BaseModel

from app.models.transaction import Transaction


# the running position at one point in the chronological replay
class SpendState(BaseModel):
    true_available_balance: float
    cumulative_variable_spend: float
    percentage_consumed: float  # 0-100, against true_available_balance
    genuinely_free: float
    daily_allowance: float
    days_elapsed: int
    days_remaining: int
    transaction_history: list[Transaction]  # everything seen up to and including this point
