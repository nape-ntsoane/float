from app.constants.buckets import Bucket
from app.constants.thresholds import (
    IMPULSE_ABSOLUTE_FLOOR,
    IMPULSE_MINIMUM_SAMPLE,
    IMPULSE_MULTIPLIER,
    UNUSUAL_CATEGORY_ID,
)
from app.models.enums import Severity
from app.models.notification import Notification
from app.models.state import SpendState
from app.models.transaction import Transaction
from app.services.message_composer import MessageComposer


class ImpulseRule:
    def __init__(self, composer: MessageComposer) -> None:
        self.composer = composer

    def evaluate(self, state: SpendState, transaction: Transaction) -> list[Notification]:
        if transaction.bucket != Bucket.variable:
            return []  # fixed/committed spend isn't a customer choice to flag

        is_unusual = transaction.category_id == UNUSUAL_CATEGORY_ID
        mean = self._mean_variable_transaction(state, transaction)
        floor = IMPULSE_ABSOLUTE_FLOOR  # used until the mean is trustworthy
        threshold = floor if mean is None else mean * IMPULSE_MULTIPLIER
        
        if abs(transaction.amount) <= threshold and not is_unusual:
            return []  # either condition alone is enough to flag

        return [
            Notification(
                severity=Severity.warning,
                triggering_rule="impulse",
                triggering_event=transaction.transaction_id,
                timestamp=transaction.transaction_date,
                message=self.composer.compose_impulse_message(transaction, mean, is_unusual),
            )
        ]

    def _mean_variable_transaction(
        self, state: SpendState, transaction: Transaction
    ) -> float | None:
        variable = [  # excludes the one being judged, so it can't inflate its own threshold
            t
            for t in state.transaction_history
            if t.bucket == Bucket.variable and t.transaction_id != transaction.transaction_id
        ]
        
        if len(variable) < IMPULSE_MINIMUM_SAMPLE:
            return None  # too few to trust yet - caller falls back to the flat floor
        
        return sum(abs(t.amount) for t in variable) / len(variable)
