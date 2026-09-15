from app.constants.thresholds import PROJECTION_TRAILING_WINDOWS_DAYS
from app.models.enums import Severity
from app.models.notification import Notification
from app.models.state import SpendState
from app.models.transaction import Transaction
from app.services.message_composer import MessageComposer
from app.utils.math_utils import burn_rate


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
        rate = burn_rate(
            state.transaction_history, transaction.transaction_date, window_days, state.days_elapsed
        )
        return transaction.running_balance - (rate * state.days_remaining)
