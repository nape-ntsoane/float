from app.constants.thresholds import THRESHOLD_LEVELS
from app.models.enums import Severity
from app.models.notification import Notification
from app.models.state import SpendState
from app.models.transaction import Transaction
from app.services.message_composer import MessageComposer


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
                        message=self.composer.compose_threshold_message(level, state),
                    )
                )
        return findings

    # 50/75 are a heads up, 90/95 mean real risk of ending the month short
    def _severity_for(self, level: int) -> Severity:
        if level >= 90:
            return Severity.critical
        if level >= 75:
            return Severity.warning
        return Severity.informational
