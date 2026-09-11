from datetime import date

from pydantic import BaseModel


class DailySalesResponse(BaseModel):
    date: date
    orders: int
    revenue: int