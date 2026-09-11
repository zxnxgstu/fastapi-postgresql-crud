from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrderStatusHistoryResponse(BaseModel):
    id: int
    order_id: int
    old_status: str | None
    new_status: str
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)