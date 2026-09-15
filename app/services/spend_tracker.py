from app.constants.buckets import Bucket
from app.models.state import SpendState
from app.models.transaction import Account, Transaction
from app.utils.date_utils import days_elapsed, days_remaining


class SpendStateTracker:
    # true_available_balance is fixed for the period - pass in what BalanceService computed
    def __init__(self, account: Account, true_available_balance: float) -> None:
        self.account = account
        self.true_available_balance = true_available_balance
        self.cumulative_variable_spend = 0.0
        self.transaction_history: list[Transaction] = []

    # updates running state for one transaction and returns the state at that point
    def apply(self, transaction: Transaction) -> SpendState:
        self.transaction_history.append(transaction)

        # amounts are signed - a refund returns spending capacity, so it
        # reduces spend rather than counting as fresh income
        if transaction.bucket == Bucket.variable:
            self.cumulative_variable_spend += abs(transaction.amount)
        elif transaction.bucket == Bucket.credit_back:
            self.cumulative_variable_spend -= abs(transaction.amount)

        genuinely_free = self.true_available_balance - self.cumulative_variable_spend
        remaining = days_remaining(
            self.account.period_start, self.account.period_end, transaction.transaction_date
        )

        return SpendState(
            true_available_balance=self.true_available_balance,
            cumulative_variable_spend=self.cumulative_variable_spend,
            percentage_consumed=self.cumulative_variable_spend / self.true_available_balance * 100,
            genuinely_free=genuinely_free,
            # no days left on the period's last day, so there's nothing to divide by
            daily_allowance=genuinely_free / remaining if remaining > 0 else genuinely_free,
            days_elapsed=days_elapsed(self.account.period_start, transaction.transaction_date),
            days_remaining=remaining,
            
            transaction_history=list(self.transaction_history),  # copied, so it won't grow later
        )
