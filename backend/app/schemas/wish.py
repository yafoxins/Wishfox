from __future__ import annotations

from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import WishPriority, WishStatus


class WishBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=2048)
    url: str | None = Field(default=None, max_length=512)
    price: Decimal | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=512)
    priority: WishPriority = WishPriority.MEDIUM
    status: WishStatus = WishStatus.PLANNED
    tags: List[str] = Field(default_factory=list)


class WishCreate(WishBase):
    wishlist_id: int


class WishUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=2048)
    url: str | None = Field(default=None, max_length=512)
    price: Decimal | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=512)
    priority: WishPriority | None = None
    status: WishStatus | None = None
    tags: List[str] | None = None
    position: int | None = Field(default=None, ge=0)


class WishReorderItem(BaseModel):
    id: int
    position: int = Field(..., ge=0)


class WishRead(WishBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wishlist_id: int
    position: int
