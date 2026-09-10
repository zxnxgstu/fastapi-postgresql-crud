from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    price: int
    in_stock: bool


class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    in_stock: bool

    model_config = ConfigDict(from_attributes=True)