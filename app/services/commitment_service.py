import uuid
from datetime import datetime

from app.models.commitment import Commitment
from app.models.enums import CommitmentType
from app.repositories.commitment import CommitmentRepository


class CommitmentService:
    def __init__(self, repository: CommitmentRepository) -> None:
        self.repository = repository

    def declare(
        self,
        commitment_type: CommitmentType,
        scope: str,
        window_start: datetime,
        window_end: datetime,
        target_value: float | None,
    ) -> Commitment:
        commitment = Commitment(
            id=str(uuid.uuid4()),
            type=commitment_type,
            scope=scope,
            target_value=target_value,
            window_start=window_start,
            window_end=window_end,
            created_at=window_start,
        )
        return self.repository.add(commitment)
