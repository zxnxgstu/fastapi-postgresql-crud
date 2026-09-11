from pydantic import BaseModel, ConfigDict, Field


class PromoCodeCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    discount_percent: int = Field(ge=1, le=100)
    active: bool = True


class PromoCodeResponse(BaseModel):
    id: int
    code: str
    discount_percent: int
    active: bool

    model_config = ConfigDict(from_attributes=True)