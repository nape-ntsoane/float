from app.models.notification import Notification
from app.repositories.transaction import TransactionRepository
from app.rules.threshold_rule import ThresholdRule
from app.services.balance_service import BalanceService
from app.services.classification_service import ClassificationService
from app.services.spend_tracker import SpendStateTracker


class EventLoop:
    # a list - each rule is called and read the same way regardless of which ones are active
    def __init__(self, repository: TransactionRepository, rules: list[ThresholdRule]) -> None:
        self.repository = repository
        self.rules = rules

    # replays the period chronologically, one transaction at a time
    def run(self) -> list[Notification]:
        account = self.repository.load_account()
        transactions = self.repository.load_transactions()

        # true_available_balance needs every transaction classified first
        ClassificationService().classify_all(transactions)
        true_available = BalanceService().compute_true_available(transactions)
        tracker = SpendStateTracker(account, true_available)

        notifications: list[Notification] = []
        for transaction in transactions:
            state = tracker.apply(transaction)
            for rule in self.rules:
                notifications.extend(rule.evaluate(state, transaction))
        return notifications
