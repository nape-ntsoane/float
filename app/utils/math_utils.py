from datetime import datetime, timedelta

from app.constants.buckets import Bucket
from app.constants.thresholds import PROJECTION_TRAILING_WINDOWS_DAYS
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


# worst and best case closing balance across the trailing windows plus month-to-date
def projected_range(
    transaction_history: list[Transaction],
    running_balance: float,
    as_of: datetime,
    days_elapsed: int,
    days_remaining: int,
) -> tuple[float, float]:
    windows = [*PROJECTION_TRAILING_WINDOWS_DAYS, days_elapsed]
    rates = [burn_rate(transaction_history, as_of, window, days_elapsed) for window in windows]
    projections = [running_balance - rate * days_remaining for rate in rates]
    return min(projections), max(projections)
