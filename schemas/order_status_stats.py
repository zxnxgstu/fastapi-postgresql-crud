from pydantic import BaseModel


class OrderStatusStatsResponse(BaseModel):
    status: str
    orders: int