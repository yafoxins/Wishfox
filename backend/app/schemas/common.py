from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Pagination(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)


class Paginated(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int


class Message(BaseModel):
    detail: str
