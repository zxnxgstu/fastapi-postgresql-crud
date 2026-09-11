from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: int = Field(ge=0)
    in_stock: bool
    category_id: int | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    in_stock: bool
    category_id: int | None = None

    model_config = ConfigDict(from_attributes=True)