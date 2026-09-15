from app.models.enums import CommandType
from app.models.state import SpendState
from app.repositories.transaction import TransactionRepository
from app.schemas.chat import InboundMessage, OutboundMessage
from app.services.balance_service import BalanceService
from app.services.classification_service import ClassificationService
from app.services.intention_service import IntentionEvaluationService
from app.services.message_composer import MessageComposer
from app.services.spend_tracker import SpendStateTracker

MENU_OPTIONS = ["Check my position", "Can I afford something?"]


class InteractionHandler:
    def __init__(
        self,
        repository: TransactionRepository,
        intention_service: IntentionEvaluationService,
        composer: MessageComposer,
    ) -> None:
        self.repository = repository
        self.intention_service = intention_service
        self.composer = composer

    def handle(self, message: InboundMessage) -> OutboundMessage:
        if message.command_type == CommandType.query_position:
            return self._query_position()
        if message.command_type == CommandType.intention_check:
            return self._intention_check(message.payload)
        
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

    # recomputed fresh each call - no session or cache, just the one fixed dataset
    def _current_state(self) -> SpendState:
        account = self.repository.load_account()
        transactions = self.repository.load_transactions()
        ClassificationService().classify_all(transactions)
        true_available = BalanceService().compute_true_available(transactions)
        tracker = SpendStateTracker(account, true_available)

        state = None
        for transaction in transactions:
            state = tracker.apply(transaction)
        assert state is not None  # the dataset always has transactions
        
        return state
