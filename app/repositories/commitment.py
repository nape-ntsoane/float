from app.models.commitment import Commitment
from app.models.enums import CommitmentStatus


class CommitmentRepository:
    def __init__(self) -> None:
        self.commitments: dict[str, Commitment] = {}

    def add(self, commitment: Commitment) -> Commitment:
        self.commitments[commitment.id] = commitment
        return commitment

    def get(self, commitment_id: str) -> Commitment | None:
        return self.commitments.get(commitment_id)

    def list_active(self) -> list[Commitment]:
        return [c for c in self.commitments.values() if c.status == CommitmentStatus.active]
