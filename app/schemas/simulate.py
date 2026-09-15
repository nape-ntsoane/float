from pydantic import BaseModel


class SimulateRequest(BaseModel):
    amount: float  # positive rand value of the hypothetical purchase
    category_id: int
    narrative: str = ""
