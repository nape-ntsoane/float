from pathlib import Path

from app.core.config import settings
from app.engine.event_loop import EventLoop
from app.engine.interaction_handler import InteractionHandler
from app.repositories.commitment import CommitmentRepository
from app.repositories.transaction import TransactionRepository
from app.rules.commitment_rule import CommitmentRule
from app.rules.impulse_rule import ImpulseRule
from app.rules.projection_rule import ProjectionRule
from app.rules.recognition_rule import RecognitionRule
from app.rules.rule import Rule
from app.rules.threshold_rule import ThresholdRule
from app.services.commitment_service import CommitmentService
from app.services.health_service import HealthService
from app.services.intention_service import IntentionEvaluationService
from app.services.message_composer import MessageComposer

# shared across requests, not per-request
_commitment_repository = CommitmentRepository()


def get_health_service() -> HealthService:
    return HealthService()


def get_event_loop() -> EventLoop:
    repository = TransactionRepository(Path(settings.data_file_path))
    composer = MessageComposer()
    rules: list[Rule] = [
        ThresholdRule(composer),
        ImpulseRule(composer),
        ProjectionRule(composer),
        RecognitionRule(composer),
        CommitmentRule(_commitment_repository, composer),
    ]
    return EventLoop(repository, _commitment_repository, rules)


def get_interaction_handler() -> InteractionHandler:
    repository = TransactionRepository(Path(settings.data_file_path))
    commitment_service = CommitmentService(_commitment_repository)
    return InteractionHandler(
        repository, IntentionEvaluationService(), commitment_service, MessageComposer()
    )
