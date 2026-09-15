from app.models.enums import Severity
from app.models.notification import Notification
from app.models.state import SpendState
from app.models.transaction import Transaction
from app.services.message_composer import MessageComposer
from app.utils.math_utils import projected_range


class ProjectionRule:
    def __init__(self, composer: MessageComposer) -> None:
        self.composer = composer
        self.was_negative: bool | None = None  # so the first read always reports a baseline

    # fires only when the worst-case projection flips sign - that's the newsworthy moment
    def evaluate(self, state: SpendState, transaction: Transaction) -> list[Notification]:
        low, high = projected_range(
            state.transaction_history,
            transaction.running_balance,
            transaction.transaction_date,
            state.days_elapsed,
            state.days_remaining,
        )

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
