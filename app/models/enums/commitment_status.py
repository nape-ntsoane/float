import enum


class CommitmentStatus(enum.StrEnum):
    active = "ACTIVE"
    upheld = "UPHELD"
    broken = "BROKEN"
    expired = "EXPIRED"
    cancelled = "CANCELLED"
