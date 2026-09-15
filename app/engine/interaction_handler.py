from datetime import datetime

from app.engine.replay import prepare_replay
from app.models.enums import CommandType, CommitmentType
from app.models.state import SpendState
from app.repositories.transaction import TransactionRepository
from app.schemas.chat import InboundMessage, OutboundMessage
from app.services.commitment_service import CommitmentService
from app.services.intention_service import IntentionEvaluationService
from app.services.message_composer import MessageComposer

MENU_OPTIONS = ["Check my position", "Can I afford something?", "Make a commitment"]


class InteractionHandler:
    def __init__(
        self,
        repository: TransactionRepository,
        intention_service: IntentionEvaluationService,
        commitment_service: CommitmentService,
        composer: MessageComposer,
    ) -> None:
        self.repository = repository
        self.intention_service = intention_service
        self.commitment_service = commitment_service
        self.composer = composer

    def handle(self, message: InboundMessage) -> OutboundMessage:
        if message.command_type == CommandType.query_position:
            return self._query_position()
        if message.command_type == CommandType.intention_check:
            return self._intention_check(message.payload)
        if message.command_type == CommandType.declare_commitment:
            return self._declare_commitment(message.payload)
        return OutboundMessage(message="I didn't understand that.", options=MENU_OPTIONS)

    def _query_position(self) -> OutboundMessage:
        state = self._current_state()

        return OutboundMessage(
            message=self.composer.compose_position_message(state), options=MENU_OPTIONS
        )

    def _intention_check(self, payload: dict) -> OutboundMessage:
        state = self._current_state()
        result = self.intention_service.evaluate(state, payload["amount"])

        return OutboundMessage(
            message=self.composer.compose_intention_message(result), options=MENU_OPTIONS
        )

    # window dates come from the client rather than "now"
    def _declare_commitment(self, payload: dict) -> OutboundMessage:
        self.commitment_service.declare(
            commitment_type=CommitmentType(payload["type"]),
            scope=payload["scope"],
            window_start=datetime.fromisoformat(payload["window_start"]),
            window_end=datetime.fromisoformat(payload["window_end"]),
            target_value=payload.get("target_value"),
        )
        return OutboundMessage(message="Got it - I'll hold you to that.", options=MENU_OPTIONS)

    # recomputed fresh each call - no session or cache, just the one fixed dataset
    def _current_state(self) -> SpendState:
        transactions, tracker = prepare_replay(self.repository, self.commitment_service.repository)

        state = None
        for transaction in transactions:
            state = tracker.apply(transaction)
        assert state is not None  # the dataset always has transactions
        return state
