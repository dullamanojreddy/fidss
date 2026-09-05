from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field

UserRole = Literal["OFFICER", "SENIOR_OFFICER", "ADMIN"]


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    full_name: str
    role: UserRole
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
