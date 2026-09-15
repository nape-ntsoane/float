from app.models.state import SpendState


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
