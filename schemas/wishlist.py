from pydantic import BaseModel, ConfigDict


class WishlistItemCreate(BaseModel):
    product_id: int


class WishlistItemResponse(BaseModel):
    id: int
    product_id: int

    model_config = ConfigDict(from_attributes=True)