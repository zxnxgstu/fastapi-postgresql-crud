from pydantic import BaseModel


class AdminStatsResponse(BaseModel):
    total_users: int
    total_products: int
    total_orders: int
    completed_orders: int
    total_revenue: int