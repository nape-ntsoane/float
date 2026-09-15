from app.constants.thresholds import THRESHOLD_LEVELS
from app.models.enums import Severity
from app.models.notification import Notification
from app.models.state import SpendState
from app.models.transaction import Transaction
from app.services.message_composer import MessageComposer
from app.utils.math_utils import projected_range

# the level that also gets a projected close in its message - see compose_threshold_message
LEVEL_WITH_PROJECTION = 95


class ThresholdRule:
    def __init__(self, composer: MessageComposer) -> None:
        self.composer = composer

        # fires once per level per period - re-firing on every later transaction would be noise
        self.fired: set[int] = set()

    # checks every level on every transaction
    # one large transaction can push percentage_consumed past two levels at once
    def evaluate(self, state: SpendState, transaction: Transaction) -> list[Notification]:
        findings = []
        for level in THRESHOLD_LEVELS:
            if level not in self.fired and state.percentage_consumed >= level:
                self.fired.add(level)
                findings.append(
                    Notification(
                        severity=self._severity_for(level),
                        triggering_rule="threshold",
                        triggering_event=transaction.transaction_id,
                        timestamp=transaction.transaction_date,
                        message=self._compose(level, state, transaction),
                    )
                )
        return findings

    # composes a message for the level, optionally including a projected close if it's the highest level
    def _compose(self, level: int, state: SpendState, transaction: Transaction) -> str:
        if level != LEVEL_WITH_PROJECTION:
            return self.composer.compose_threshold_message(level, state)
        low, high = projected_range(
            state.transaction_history,
            transaction.running_balance,
            transaction.transaction_date,
            state.days_elapsed,
            state.days_remaining,
        )
        return self.composer.compose_threshold_message(level, state, projected_range=(low, high))

    # 50/75 are a heads up, 90/95 mean real risk of ending the month short
    def _severity_for(self, level: int) -> Severity:
        if level >= 90:
            return Severity.critical
        if level >= 75:
            return Severity.warning
        return Severity.informational
