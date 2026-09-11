from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class OrderItemResponse(BaseModel):
    id: int
    product_id: int | None
    product_name: str
    price: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    shipping_city: str
    shipping_street: str
    shipping_postal_code: str

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: int
    status: str
    created_at: datetime
    shipping_city: str | None
    shipping_street: str | None
    shipping_postal_code: str | None
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: Literal[
        "pending",
        "paid",
        "shipped",
        "completed",
        "cancelled"
    ]