from app.constants.buckets import Bucket
from app.constants.categories import (
    CATEGORY_BUCKETS,
    FAMILY_SUPPORT_NARRATIVE,
    SAVINGS_POCKET_NARRATIVE,
    TRANSFERS_CATEGORY_ID,
)
from app.models.transaction import Transaction


class ClassificationService:
    # looks up the bucket by category id, falling back to the transfer sub-rule for category 104
    def classify(self, transaction: Transaction) -> Bucket:
        if transaction.category_id == TRANSFERS_CATEGORY_ID:
            return self._classify_transfer(transaction)
        return CATEGORY_BUCKETS[transaction.category_id]

    # classifies every transaction in place and returns them
    def classify_all(self, transactions: list[Transaction]) -> list[Transaction]:
        for transaction in transactions:
            transaction.bucket = self.classify(transaction)
        return transactions

    # narrative-based sub-rule for category 104 (transfers)
    def _classify_transfer(self, transaction: Transaction) -> Bucket:
        # source data is already uppercase, but normalise rather than rely on that
        narrative = transaction.narrative.upper()
        if SAVINGS_POCKET_NARRATIVE in narrative or FAMILY_SUPPORT_NARRATIVE in narrative:
            return Bucket.committed
        return Bucket.variable
