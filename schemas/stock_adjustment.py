from pydantic import BaseModel, Field


class StockAdjustmentRequest(BaseModel):
    quantity_change: int = Field(ne=0)
    reason: str = Field(min_length=1, max_length=100)