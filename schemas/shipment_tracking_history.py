from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ShipmentTrackingHistoryResponse(BaseModel):
    id: int
    order_id: int
    shipping_carrier: str
    tracking_number: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)