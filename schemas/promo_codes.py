from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PromoCodeCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    discount_percent: int = Field(ge=1, le=100)
    active: bool = True

    expires_at: datetime | None = None
    min_order_amount: int = Field(default=0, ge=0)
    max_uses: int | None = Field(default=None, ge=1)

class PromoCodeUpdate(BaseModel):
    discount_percent: int | None = Field(
        default=None,
        ge=1,
        le=100
    )
    active: bool | None = None
    expires_at: datetime | None = None
    min_order_amount: int | None = Field(
        default=None,
        ge=0
    )
    max_uses: int | None = Field(
        default=None,
        ge=1
    )

class PromoCodeResponse(BaseModel):
    id: int
    code: str
    discount_percent: int
    active: bool

    expires_at: datetime | None
    min_order_amount: int
    max_uses: int | None
    used_count: int

    model_config = ConfigDict(from_attributes=True)