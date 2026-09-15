from app.constants.buckets import Bucket
from app.models.enums import Severity
from app.models.notification import Notification
from app.models.state import SpendState
from app.models.transaction import Transaction
from app.services.message_composer import MessageComposer


class RecognitionRule:
    def __init__(self, composer: MessageComposer) -> None:
        self.composer = composer
        # at most one recognition per category per period
        self.recognised_categories: set[int] = set()

    # checks every variable category on every transaction, not just the current one's own
    # silence is only detectable by however much time has passed since something last happened
    def evaluate(self, state: SpendState, transaction: Transaction) -> list[Notification]:
        by_category = self._variable_by_category(state)
        findings = []
        for category_id, history in by_category.items():
            if category_id in self.recognised_categories or len(history) < 2:
                continue
            days_since = (transaction.transaction_date - history[-1].transaction_date).days
            if days_since > self._silence_threshold(history):
                self.recognised_categories.add(category_id)
                findings.append(self._recognise(history[-1].category_name, days_since, transaction))
        return findings

    def _variable_by_category(self, state: SpendState) -> dict[int, list[Transaction]]:
        by_category: dict[int, list[Transaction]] = {}
        for t in state.transaction_history:
            if t.bucket == Bucket.variable:
                by_category.setdefault(t.category_id, []).append(t)
        return by_category

    # a gap this far outside the category's own history, seen so far, is worth noticing
    def _silence_threshold(self, history: list[Transaction]) -> float:
        gaps = [
            (b.transaction_date - a.transaction_date).days
            for a, b in zip(history, history[1:], strict=False)  # one shorter by design
        ]
        mean_gap = sum(gaps) / len(gaps)
        return max(2 * mean_gap, max(gaps) + 1)

    def _recognise(
        self, category_name: str, days_since: int, transaction: Transaction
    ) -> Notification:
        return Notification(
            severity=Severity.recognition,
            triggering_rule="recognition",
            triggering_event=transaction.transaction_id,
            timestamp=transaction.transaction_date,
            message=self.composer.compose_recognition_message(category_name, days_since),
        )
