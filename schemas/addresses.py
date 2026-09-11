from pydantic import BaseModel, ConfigDict, Field


class AddressCreate(BaseModel):
    city: str = Field(min_length=1, max_length=100)
    street: str = Field(min_length=1, max_length=200)
    postal_code: str = Field(min_length=1, max_length=30)
    is_default: bool = False


class AddressUpdate(BaseModel):
    city: str = Field(min_length=1, max_length=100)
    street: str = Field(min_length=1, max_length=200)
    postal_code: str = Field(min_length=1, max_length=30)
    is_default: bool = False


class AddressResponse(BaseModel):
    id: int
    user_id: int
    city: str
    street: str
    postal_code: str
    is_default: bool

    model_config = ConfigDict(from_attributes=True)