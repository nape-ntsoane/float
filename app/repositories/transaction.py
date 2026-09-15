import json
from pathlib import Path
from typing import Any

from app.models.enums import Direction
from app.models.transaction import Account, Transaction


class TransactionRepository:
    # reads the whole file once, both loaders below read from this
    def __init__(self, data_path: Path) -> None:
        self.data: dict[str, Any] = json.loads(data_path.read_text())

    # parses the account block
    def load_account(self) -> Account:
        account = self.data["account"]
        return Account(
            identifier=account["accountId"],
            currency=account["currency"],
            opening_balance=account["openingBalance"]["amount"],
            period_start=account["statementPeriod"]["from"],
            period_end=account["statementPeriod"]["to"],
        )

    # sorted explicitly - chronological order is relied on downstream
    def load_transactions(self) -> list[Transaction]:
        transactions = [self._to_transaction(line) for line in self.data["statementLines"]]
        return sorted(transactions, key=lambda t: t.transaction_date)

    # maps one raw statement line to a Transaction
    def _to_transaction(self, line: dict[str, Any]) -> Transaction:
        return Transaction(
            transaction_id=line["transactionId"],
            transaction_date=line["transactionDate"],
            amount=line["amount"]["amount"],
            direction=Direction(line["transactionType"]),
            category_id=line["transactionCategory"]["transactionCategoryId"],
            category_name=line["transactionCategory"]["transactionCategoryName"],
            narrative=line["narrative"],
            running_balance=line["runningBalance"]["amount"],
        )
