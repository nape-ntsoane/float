from app.constants.thresholds import PROJECTION_TRAILING_WINDOWS_DAYS
from app.models.enums import IntentionVerdict
from app.models.intention import IntentionResult
from app.models.state import SpendState
from app.utils.math_utils import burn_rate


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
        windows = [*PROJECTION_TRAILING_WINDOWS_DAYS, state.days_elapsed]
        projections = [
            last.running_balance - rate * state.days_remaining
            for rate in (
                burn_rate(state.transaction_history, last.transaction_date, w, state.days_elapsed)
                for w in windows
            )
        ]
        return min(projections)

    def _days_until_affordable(self, state: SpendState, amount: float) -> float | None:
        if state.daily_allowance <= 0:
            return None
        return amount / state.daily_allowance  # a same-period estimate - one month of data only
