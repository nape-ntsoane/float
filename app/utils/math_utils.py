from datetime import datetime, timedelta

from app.constants.buckets import Bucket
from app.models.transaction import Transaction


# average daily variable spend in the trailing window_days ending at as_of
def burn_rate(
    transaction_history: list[Transaction], as_of: datetime, window_days: int, days_elapsed: int
) -> float:
    cutoff = as_of - timedelta(days=window_days)

    in_window = [
        t
        for t in transaction_history
        if t.bucket == Bucket.variable and t.transaction_date >= cutoff
    ]
    if not in_window:
        return 0.0
    
    actual_days = min(window_days, days_elapsed)
    return sum(abs(t.amount) for t in in_window) / actual_days
