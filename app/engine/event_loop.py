from app.constants.categories import CATEGORY_NAMES
from app.engine.replay import prepare_replay
from app.models.enums import Direction, SettlementStatus
from app.models.notification import Notification
from app.models.transaction import Transaction
from app.repositories.commitment import CommitmentRepository
from app.repositories.transaction import TransactionRepository
from app.rules.commitment_rule import CommitmentRule
from app.rules.rule import Rule
from app.services.classification_service import ClassificationService


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

    # replays the real month first (silently, so every rule reaches a realistic
    # fired/seen state), then evaluates one hypothetical purchase on top of that
    def simulate(self, amount: float, category_id: int, narrative: str) -> list[Notification]:
        # CommitmentRule mutates commitment status on the shared repository, which a
        # hypothetical check must never do - every other rule's state is a fresh
        safe_rules = [rule for rule in self.rules if not isinstance(rule, CommitmentRule)]

        transactions, tracker = prepare_replay(self.repository, self.commitment_repository)
        for transaction in transactions:
            state = tracker.apply(transaction)
            for rule in safe_rules:
                rule.evaluate(state, transaction)

        last = transactions[-1]
        hypothetical = Transaction(
            transaction_id="SIMULATED",
            transaction_date=last.transaction_date,
            amount=-abs(amount),
            direction=Direction.debit,
            category_id=category_id,
            category_name=CATEGORY_NAMES[category_id],
            narrative=narrative,
            running_balance=last.running_balance - abs(amount),
            settlement_status=SettlementStatus.provisional,
        )
        hypothetical.bucket = ClassificationService().classify(hypothetical)
        state = tracker.apply(hypothetical)

        findings: list[Notification] = []
        for rule in safe_rules:
            findings.extend(rule.evaluate(state, hypothetical))
        return findings
