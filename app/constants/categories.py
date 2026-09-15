"""Category identifiers and their bucket assignments, transcribed from the
Technical Design (plan/07_Technical_Design.md, Section 7). Every value here
is a design decision recorded in that document, not a code fix - changing a
bucket assignment means updating the design doc first.
"""

from app.constants.buckets import Bucket

CATEGORY_NAMES: dict[int, str] = {
    100: "Income / Salary",
    101: "Groceries",
    102: "Transport",
    103: "Subscriptions",
    104: "Transfers",
    105: "Cash Withdrawal",
    106: "Online Purchases",
    107: "Discretionary Spending",
    108: "Once-off Large Purchase",
    109: "Refund / Reversal",
    110: "Fixed Commitments",
    111: "Debit Order",
    112: "Bank Fees",
    199: "Uncategorised / Unusual",
}

TRANSFERS_CATEGORY_ID = 104
"""The one category with no static bucket - see CATEGORY_BUCKETS below."""

CATEGORY_BUCKETS: dict[int, Bucket] = {
    100: Bucket.income,
    101: Bucket.variable,
    102: Bucket.variable,
    103: Bucket.variable,  # D1 - discretionary and individually cancellable
    # 104 (Transfers) is intentionally absent: its bucket depends on the
    # transaction's narrative, not its category ID alone. See the sub-rule
    # constants below and ClassificationService, which applies them.
    105: Bucket.variable,
    106: Bucket.variable,
    107: Bucket.variable,
    108: Bucket.variable,
    109: Bucket.credit_back,
    110: Bucket.committed,
    111: Bucket.committed,
    112: Bucket.variable,  # D2 - visible as a consequence of customer behaviour
    199: Bucket.variable,  # also always raises an impulse flag - see R2
}

# Narrative sub-rule for category 104 (Transfers) - Section 7. A transfer
# whose narrative contains either string below is COMMITTED; any other
# transfer is VARIABLE. Matched by ClassificationService - this module holds
# only the literal strings the design document specifies.
SAVINGS_POCKET_NARRATIVE = "SAVINGS POCKET"
FAMILY_SUPPORT_NARRATIVE = "FAMILY SUPPORT"
