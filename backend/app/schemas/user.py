from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    display_name: str = Field(..., max_length=255)
    username: str = Field("", max_length=255)
    tg_username: str | None = None
    custom_username: str | None = None
    avatar_url: str | None = None
    bio: str | None = Field(default=None, max_length=512)
    locale: str | None = Field(default="en", max_length=8)
    requires_custom_username: bool = False

    @model_validator(mode="before")
    @classmethod
    def compute_username(cls, data: dict) -> dict:
        if isinstance(data, dict):
            username = data.get("username")
            tg_username = data.get("tg_username")
            custom_username = data.get("custom_username")
            if not username:
                data["username"] = tg_username or custom_username or ""
            data["requires_custom_username"] = tg_username is None and not custom_username
        return data


class UserMe(UserBase):
    pass


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    display_name: str
    username: str
    avatar_url: str | None = None
    bio: str | None = None

    # Compute username from available fields (tg_username/custom_username)
    # for cases when the ORM instance doesn't have a consolidated "username" attribute.
    @model_validator(mode="before")
    @classmethod
    def ensure_username(cls, data):
        # Accept both dicts and ORM objects
        if isinstance(data, dict):
            username = data.get("username") or data.get("tg_username") or data.get("custom_username") or ""
            data["username"] = username
            return data
        # Fallback for SQLAlchemy model instances
        try:
            username = (
                getattr(data, "username", None)
                or getattr(data, "tg_username", None)
                or getattr(data, "custom_username", None)
                or ""
            )
            return {
                "id": getattr(data, "id"),
                "display_name": getattr(data, "display_name"),
                "username": username,
                "avatar_url": getattr(data, "avatar_url", None),
                "bio": getattr(data, "bio", None),
            }
        except Exception:
            return data


class UserUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=512)
    avatar_url: str | None = Field(default=None, max_length=512)
    custom_username: str | None = Field(default=None, max_length=255)
    locale: str | None = Field(default=None, max_length=8)
