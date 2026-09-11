from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    quantity_change: int
    reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)