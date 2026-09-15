"""Numeric thresholds fixed by the Technical Design (Section 9) and the
Curveball integration (Section 4/06_Curveball_Integration.md). Every value
here was chosen deliberately and justified in the design doc - do not tune
these without updating it first.
"""

IMPULSE_MULTIPLIER = 2.5
"""R2 - a transaction over this multiple of the customer's own mean variable
transaction is flagged. Evidence-backed against the dataset - see Section 9."""

IMPULSE_MINIMUM_SAMPLE = 5
"""D3 - the impulse rule needs at least this many observed variable
transactions before it trusts its own mean; below this it falls back to
IMPULSE_ABSOLUTE_FLOOR so the rule isn't unstable in the first few days."""

IMPULSE_ABSOLUTE_FLOOR = 500.0
"""D3 - conservative flat rand threshold used only before
IMPULSE_MINIMUM_SAMPLE is reached."""

UNUSUAL_CATEGORY_ID = 199
"""Always raises an impulse flag regardless of amount - Section 7."""

THRESHOLD_LEVELS: list[int] = [50, 75, 90, 95]
"""R4 - percentage-of-True-Available-Balance levels that fire an escalating
notification, each exactly once per period (D5)."""

PROJECTION_TRAILING_WINDOWS_DAYS: list[int] = [7, 14]
"""R3 - the two trailing burn-rate windows. The third window is
month-to-date and has no fixed length, so it isn't listed here."""
