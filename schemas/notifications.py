from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PriceDropNotificationResponse(BaseModel):
    id: int
    product_id: int
    old_price: int
    new_price: int
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)