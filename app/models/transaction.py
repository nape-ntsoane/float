from datetime import datetime

from pydantic import BaseModel

from app.models.enums import Direction, SettlementStatus


# one statement line, parsed from Transaction_DP.txt
class Transaction(BaseModel):
    transaction_id: str
    transaction_date: datetime
    amount: float  # signed: positive credit, negative debit
    direction: Direction
    category_id: int
    category_name: str
    narrative: str
    running_balance: float
    
    # provisional = a declared intention, not a real transaction yet
    settlement_status: SettlementStatus = SettlementStatus.settled


# the case study's account block
class Account(BaseModel):
    identifier: str
    currency: str
    opening_balance: float
    period_start: datetime
    period_end: datetime
