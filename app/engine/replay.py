from app.models.transaction import Transaction
from app.repositories.commitment import CommitmentRepository
from app.repositories.transaction import TransactionRepository
from app.services.balance_service import BalanceService
from app.services.classification_service import ClassificationService
from app.services.spend_tracker import SpendStateTracker


# loads and classifies the period's transactions, and builds a tracker ready to replay them -
# shared by EventLoop (replays every transaction) and InteractionHandler (wants only final state)
def prepare_replay(
    repository: TransactionRepository, commitment_repository: CommitmentRepository
) -> tuple[list[Transaction], SpendStateTracker]:
    account = repository.load_account()
    transactions = repository.load_transactions()
    ClassificationService().classify_all(transactions)
    true_available = BalanceService().compute_true_available(transactions)
    tracker = SpendStateTracker(account, true_available, commitment_repository)
    return transactions, tracker
