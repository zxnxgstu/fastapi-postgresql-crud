from pydantic import BaseModel


class InventorySummaryResponse(BaseModel):
    total_products: int
    in_stock_products: int
    out_of_stock_products: int
    total_units: int
    inventory_value: int