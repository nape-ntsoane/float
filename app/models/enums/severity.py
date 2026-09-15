import enum


class Severity(enum.StrEnum):
    informational = "INFORMATIONAL"
    warning = "WARNING"
    critical = "CRITICAL"
    recognition = "RECOGNITION"
