from pydantic import BaseModel


class LowStockProductResponse(BaseModel):
    product_id: int
    name: str
    stock_quantity: int