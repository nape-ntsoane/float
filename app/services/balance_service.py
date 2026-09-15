from app.constants.buckets import Bucket
from app.models.transaction import Transaction


class BalanceService:
    # salary minus committed outflows - fixed for the period once the committed debit orders clear
    def compute_true_available(self, transactions: list[Transaction]) -> float:
        income = sum(t.amount for t in transactions if t.bucket == Bucket.income)
        
        # committed amounts are negative outflows, negate to sum as a positive total
        committed = sum(-t.amount for t in transactions if t.bucket == Bucket.committed)
        return income - committed
