"""The four buckets every transaction is classified into - Technical Design
Section 7. Fixed vocabulary the rest of the system reads; nothing should
compare a transaction's bucket against a raw string.
"""

import enum


class Bucket(enum.StrEnum):
    income = "INCOME"
    committed = "COMMITTED"
    variable = "VARIABLE"
    credit_back = "CREDIT_BACK"
