from datetime import timedelta

from app.constants.buckets import Bucket
from app.constants.thresholds import PROJECTION_TRAILING_WINDOWS_DAYS
from app.models.enums import Severity
from app.models.notification import Notification
from app.models.state import SpendState
from app.models.transaction import Transaction
from app.services.message_composer import MessageComposer


class ProjectionRule:
    def __init__(self, composer: MessageComposer) -> None:
        self.composer = composer
        self.was_negative: bool | None = None  # so the first read always reports a baseline

    # fires only when the worst-case projection flips sign - that's the newsworthy moment
    def evaluate(self, state: SpendState, transaction: Transaction) -> list[Notification]:
        windows = [*PROJECTION_TRAILING_WINDOWS_DAYS, state.days_elapsed]  # last = month-to-date
        projections = [self._project(state, transaction, window) for window in windows]
        low, high = min(projections), max(projections)

        is_negative = low < 0
        if is_negative == self.was_negative:
            return []
        self.was_negative = is_negative

        return [
            Notification(
                severity=Severity.warning if is_negative else Severity.informational,
                triggering_rule="projection",
                triggering_event=transaction.transaction_id,
                timestamp=transaction.transaction_date,
                message=self.composer.compose_projection_message(low, high),
            )
        ]

    def _project(self, state: SpendState, transaction: Transaction, window_days: int) -> float:
        burn_rate = self._burn_rate(state, transaction, window_days)
        return transaction.running_balance - (burn_rate * state.days_remaining)

    # average daily variable spend in the trailing window
    def _burn_rate(self, state: SpendState, transaction: Transaction, window_days: int) -> float:
        cutoff = transaction.transaction_date - timedelta(days=window_days)
        in_window = [
            t
            for t in state.transaction_history
            if t.bucket == Bucket.variable and t.transaction_date >= cutoff
        ]
        
        if not in_window:
            return 0.0
        actual_days = min(window_days, state.days_elapsed)  # can't exceed days elapsed so far
        return sum(abs(t.amount) for t in in_window) / actual_days
