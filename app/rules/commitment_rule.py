from app.models.commitment import Commitment
from app.models.enums import CommitmentStatus, CommitmentType, Severity
from app.models.notification import Notification
from app.models.state import SpendState
from app.models.transaction import Transaction
from app.repositories.commitment import CommitmentRepository
from app.services.message_composer import MessageComposer


class CommitmentRule:
    def __init__(self, repository: CommitmentRepository, composer: MessageComposer) -> None:
        self.repository = repository
        self.composer = composer

    # window bounds are compared by date, not exact datetime - the only clock
    # this system has is transaction events, so a boundary later in the day
    # than any transaction on that day would otherwise never be reached
    def evaluate(self, state: SpendState, transaction: Transaction) -> list[Notification]:
        findings = []
        for commitment in self.repository.list_active():
            if transaction.transaction_date.date() < commitment.window_start.date():
                continue  # not declared yet as of this transaction
            if transaction.transaction_date.date() >= commitment.window_end.date():
                findings.append(self._uphold(commitment, transaction))
                continue
            if not self._in_scope(commitment, transaction):
                continue

            broken = self._check_break(commitment, transaction)
            if broken is not None:
                findings.append(broken)
                
        return findings

    def _in_scope(self, commitment: Commitment, transaction: Transaction) -> bool:
        return commitment.scope == "general" or transaction.category_name == commitment.scope

    # earmark returns None here - it isn't breakable by a transaction,
    # only cancellation or window expiry resolves one
    def _check_break(self, commitment: Commitment, transaction: Transaction) -> Notification | None:
        if commitment.type == CommitmentType.abstain:
            return self._break(commitment, transaction)
        
        if commitment.type == CommitmentType.cap:
            commitment.cumulative_in_scope_spend += abs(transaction.amount)
            if commitment.cumulative_in_scope_spend > (commitment.target_value or 0):
                return self._break(commitment, transaction)
        
        return None

    def _break(self, commitment: Commitment, transaction: Transaction) -> Notification:
        commitment.status = CommitmentStatus.broken
        commitment.resolved_at = transaction.transaction_date
        
        return Notification(
            severity=Severity.informational,
            triggering_rule="commitment",
            triggering_event=transaction.transaction_id,
            timestamp=transaction.transaction_date,
            message=self.composer.compose_commitment_broken_message(commitment, transaction),
        )

    def _uphold(self, commitment: Commitment, transaction: Transaction) -> Notification:
        commitment.status = CommitmentStatus.upheld
        commitment.resolved_at = transaction.transaction_date
        
        return Notification(
            severity=Severity.recognition,
            triggering_rule="commitment",
            triggering_event=transaction.transaction_id,
            timestamp=transaction.transaction_date,
            message=self.composer.compose_commitment_upheld_message(commitment),
        )
