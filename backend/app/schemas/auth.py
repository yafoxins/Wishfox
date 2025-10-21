from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.user import UserMe


class AuthRequest(BaseModel):
    init_data: str = Field(..., min_length=10)


class AuthResponse(BaseModel):
    user: UserMe
    csrf_token: str
