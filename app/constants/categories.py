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

# 104 (Transfers) has no fixed bucket, it depends on the narrative - see below
CATEGORY_BUCKETS: dict[int, Bucket] = {
    100: Bucket.income,
    101: Bucket.variable,
    102: Bucket.variable,
    103: Bucket.variable,
    105: Bucket.variable,
    106: Bucket.variable,
    107: Bucket.variable,
    108: Bucket.variable,
    109: Bucket.credit_back,
    110: Bucket.committed,
    111: Bucket.committed,
    112: Bucket.variable,
    199: Bucket.variable,
}

# a transfer narrative containing either of these is COMMITTED, anything else VARIABLE
SAVINGS_POCKET_NARRATIVE = "SAVINGS POCKET"
FAMILY_SUPPORT_NARRATIVE = "FAMILY SUPPORT"
