from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)

class UserPasswordChange(BaseModel):
    current_password: str = Field(
        min_length=8,
        max_length=128
    )
    new_password: str = Field(
        min_length=8,
        max_length=128
    )

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserRoleUpdate(BaseModel):
    role: Literal["user", "admin"]

class UserActiveUpdate(BaseModel):
    is_active: bool

class RefreshSessionResponse(BaseModel):
    id: int
    created_at: datetime
    expires_at: datetime
    revoked: bool

    model_config = ConfigDict(from_attributes=True)