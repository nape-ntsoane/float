from app.engine.replay import prepare_replay
from app.models.notification import Notification
from app.repositories.commitment import CommitmentRepository
from app.repositories.transaction import TransactionRepository
from app.rules.rule import Rule


class EventLoop:
    # a list - each rule is called and read the same way regardless of which ones are active
    def __init__(
        self,
        repository: TransactionRepository,
        commitment_repository: CommitmentRepository,
        rules: list[Rule],
    ) -> None:
        self.repository = repository
        self.commitment_repository = commitment_repository
        self.rules = rules

    # replays the period chronologically, one transaction at a time
    def run(self) -> list[Notification]:
        transactions, tracker = prepare_replay(self.repository, self.commitment_repository)

        notifications: list[Notification] = []
        for transaction in transactions:
            state = tracker.apply(transaction)
            for rule in self.rules:
                notifications.extend(rule.evaluate(state, transaction))
        return notifications
