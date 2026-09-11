from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)