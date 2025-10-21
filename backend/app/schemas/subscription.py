from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserPublic


class SubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    follower_id: int
    target_user_id: int
    target: UserPublic | None = None
