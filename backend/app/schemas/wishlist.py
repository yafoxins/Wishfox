from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import WishlistVisibility
from app.schemas.wish import WishRead


class WishlistBase(BaseModel):
    title: str = Field(..., max_length=255)
    visibility: WishlistVisibility = WishlistVisibility.PUBLIC
    cover_url: str | None = Field(default=None, max_length=512)


class WishlistCreate(WishlistBase):
    pass


class WishlistRead(WishlistBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int


class WishlistDetail(WishlistRead):
    wishes: list[WishRead] = Field(default_factory=list)
