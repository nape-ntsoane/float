from datetime import datetime


# 1-indexed - the period's first day counts as day 1, not day 0
def days_elapsed(period_start: datetime, current_date: datetime) -> int:
    return (current_date.date() - period_start.date()).days + 1


def days_remaining(period_start: datetime, period_end: datetime, current_date: datetime) -> int:
    total_days = (period_end.date() - period_start.date()).days + 1
    return total_days - days_elapsed(period_start, current_date)
