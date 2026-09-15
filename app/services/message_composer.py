from app.models.enums import IntentionVerdict
from app.models.intention import IntentionResult
from app.models.state import SpendState
from app.models.transaction import Transaction


# rounded to the nearest rand and comma-formatted
def fmt(amount: float) -> str:
    return f"R{abs(round(amount)):,}"


class MessageComposer:
    def compose_threshold_message(self, level: int, state: SpendState) -> str:
        # fmt() strips the sign, so a negative genuinely_free needs its own
        # wording rather than reading as money still available
        if state.genuinely_free < 0:
            return (
                f"You've used {level}% of what's actually yours this month, "
                f"and you're already {fmt(state.genuinely_free)} over."
            )
        return (
            f"You've used {level}% of what's actually yours this month. "
            f"That leaves {fmt(state.genuinely_free)} for the next {state.days_remaining} days, "
            f"about {fmt(state.daily_allowance)} a day."
        )

    # mean is None below the minimum sample - nothing real to compare against yet
    def compose_impulse_message(
        self, transaction: Transaction, mean: float | None, is_unusual: bool
    ) -> str:
        amount = fmt(transaction.amount)
        if is_unusual:
            return f"{amount} on an unrecognised merchant or platform - worth a second look."
        if mean is None:
            return (
                f"{amount} is a large purchase this early on, "
                f"before there's much to compare it to."
            )
        multiple = abs(transaction.amount) / mean
        return f"{amount} is about {multiple:.1f}x what you'd normally spend in one go."

    # low/high are the worst and best case projected closing balances across the burn-rate windows
    def compose_projection_message(self, low: float, high: float) -> str:
        if high < 0:
            return (
                f"At your current pace, you're on track to be between {fmt(high)} and {fmt(low)} "
                f"short by the end of the month."
            )
        if low < 0:
            return (
                f"Your current pace puts you anywhere from {fmt(low)} short to {fmt(high)} ahead "
                f"by the end of the month - it could go either way."
            )
        return (
            f"You're on track to end the month between {fmt(low)} and {fmt(high)} ahead. "
            f"Keep going."
        )

    def compose_position_message(self, state: SpendState) -> str:
        if state.genuinely_free < 0:
            return (
                f"You're {fmt(state.genuinely_free)} over for the month, "
                f"{state.days_remaining} days left."
            )
        return (
            f"You've got {fmt(state.genuinely_free)} left for the next "
            f"{state.days_remaining} days, about {fmt(state.daily_allowance)} a day."
        )

    def compose_intention_message(self, result: IntentionResult) -> str:
        if result.verdict == IntentionVerdict.comfortable:
            return f"Yes - you'd still have {fmt(result.provisional_free)} left this month."
        if result.verdict == IntentionVerdict.affordable_but_risky:
            return (
                f"You can afford it right now, but it pushes you {fmt(result.provisional_close)} "
                f"short by month end."
            )
        if result.days_until_affordable is not None:
            days = round(result.days_until_affordable)
            return f"Not from what's left this month - about {days} more days."
        return "Not from what's left this month."
