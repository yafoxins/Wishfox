from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserPublic
from app.schemas.wish import WishRead


class FeedItem(BaseModel):
    actor: UserPublic
    wish: WishRead
    action: str
    created_at: datetime
