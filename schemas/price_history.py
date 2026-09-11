from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    old_price: int
    new_price: int
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)