from pydantic import BaseModel, ConfigDict, Field


class DeliveryMethodCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    price: int = Field(ge=0)
    active: bool = True


class DeliveryMethodUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: int | None = Field(default=None, ge=0)
    active: bool | None = None


class DeliveryMethodResponse(BaseModel):
    id: int
    code: str
    name: str
    price: int
    active: bool

    model_config = ConfigDict(from_attributes=True)