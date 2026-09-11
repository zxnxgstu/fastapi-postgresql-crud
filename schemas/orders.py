from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, model_validator, Field


class OrderItemResponse(BaseModel):
    id: int
    product_id: int | None
    product_name: str
    price: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    shipping_city: str | None = None
    shipping_street: str | None = None
    shipping_postal_code: str | None = None
    address_id: int | None = None
    delivery_method_id: int | None = None
    promo_code: str | None = None
    customer_note: str | None = Field(
    default=None,
    max_length=500
)

    @model_validator(mode="after")
    def validate_shipping_address(self):
        shipping_values = [
            self.shipping_city,
            self.shipping_street,
            self.shipping_postal_code
        ]

        provided_count = sum(
            value is not None
            for value in shipping_values
        )

        if provided_count not in (0, 3):
            raise ValueError(
                "Provide full shipping address"
            )

        return self

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: int
    promo_code: str | None
    discount_percent: int
    status: str
    created_at: datetime
    shipping_city: str | None
    shipping_street: str | None
    shipping_postal_code: str | None
    items: list[OrderItemResponse]
    model_config = ConfigDict(from_attributes=True)
    delivery_method_id: int | None
    delivery_method_code: str | None
    delivery_method_name: str | None
    delivery_price: int
    customer_note: str | None


class OrderStatusUpdate(BaseModel):
    status: Literal[
        "pending",
        "paid",
        "shipped",
        "completed",
        "cancelled"
    ]