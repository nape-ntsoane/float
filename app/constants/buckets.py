import enum


class Bucket(enum.StrEnum):
    income = "INCOME"
    committed = "COMMITTED"
    variable = "VARIABLE"
    credit_back = "CREDIT_BACK"
