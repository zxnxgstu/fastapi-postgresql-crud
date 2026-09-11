from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ShipmentStatus = Literal[
    "picked_up",
    "in_transit",
    "out_for_delivery",
    "delivered",
]


class ShipmentEventCreate(BaseModel):
    status: ShipmentStatus
    comment: str | None = Field(
        default=None,
        max_length=500
    )


class ShipmentEventResponse(BaseModel):
    id: int
    order_id: int
    status: str
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)