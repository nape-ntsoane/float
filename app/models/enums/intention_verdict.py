import enum


class IntentionVerdict(enum.StrEnum):
    comfortable = "COMFORTABLE"
    affordable_but_risky = "AFFORDABLE_BUT_RISKY"
    not_affordable = "NOT_AFFORDABLE"
