from typing import Protocol

from app.models.notification import Notification
from app.models.state import SpendState
from app.models.transaction import Transaction


# every rule evaluator matches this shape, so the engine loop calls them all the same way
class Rule(Protocol):
    def evaluate(self, state: SpendState, transaction: Transaction) -> list[Notification]: ...
