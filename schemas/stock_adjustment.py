from pydantic import BaseModel, Field, field_validator


class StockAdjustmentRequest(BaseModel):
    quantity_change: int
    reason: str = Field(min_length=1, max_length=100)

@field_validator("quantity_change")
@classmethod
def validate_quantity_change(cls, value: int):
    if value == 0:
        raise ValueError(
            "quantity_change must not be zero"
        )

    return value