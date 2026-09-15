from app.models.enums import IntentionVerdict
from app.models.intention import IntentionResult
from app.models.state import SpendState
from app.utils.math_utils import projected_range


class IntentionEvaluationService:
    def evaluate(self, state: SpendState, amount: float) -> IntentionResult:
        provisional_free = state.genuinely_free - amount
        provisional_close = self._projected_close(state) - amount

        if provisional_free <= 0:
            return IntentionResult(
                verdict=IntentionVerdict.not_affordable,
                provisional_free=provisional_free,
                provisional_close=provisional_close,
                days_until_affordable=self._days_until_affordable(state, amount),
            )
        if provisional_close < 0:
            return IntentionResult(
                verdict=IntentionVerdict.affordable_but_risky,
                provisional_free=provisional_free,
                provisional_close=provisional_close,
            )
        return IntentionResult(
            verdict=IntentionVerdict.comfortable,
            provisional_free=provisional_free,
            provisional_close=provisional_close,
        )

    # worst case across the same windows ProjectionRule uses - a purchase decision
    # should be checked against the most pessimistic reasonable outlook, not the average one
    def _projected_close(self, state: SpendState) -> float:
        last = state.transaction_history[-1]
        low, _ = projected_range(
            state.transaction_history,
            last.running_balance,
            last.transaction_date,
            state.days_elapsed,
            state.days_remaining,
        )
        return low

    def _days_until_affordable(self, state: SpendState, amount: float) -> float | None:
        if state.daily_allowance <= 0:
            return None
        return amount / state.daily_allowance  # a same-period estimate - one month of data only
