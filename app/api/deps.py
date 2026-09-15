from pathlib import Path

from app.core.config import settings
from app.engine.event_loop import EventLoop
from app.repositories.transaction import TransactionRepository
from app.rules.impulse_rule import ImpulseRule
from app.rules.projection_rule import ProjectionRule
from app.rules.rule import Rule
from app.rules.threshold_rule import ThresholdRule
from app.services.health_service import HealthService
from app.services.message_composer import MessageComposer


def get_health_service() -> HealthService:
    return HealthService()


def get_event_loop() -> EventLoop:
    repository = TransactionRepository(Path(settings.data_file_path))
    composer = MessageComposer()
    rules: list[Rule] = [ThresholdRule(composer), ImpulseRule(composer), ProjectionRule(composer)]
    return EventLoop(repository, rules)
