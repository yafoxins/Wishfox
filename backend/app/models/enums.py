from __future__ import annotations

from enum import Enum


class WishlistVisibility(str, Enum):
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"


class WishPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class WishStatus(str, Enum):
    PLANNED = "planned"
    ORDERED = "ordered"
    GIFTED = "gifted"


class NotificationType(str, Enum):
    WISH_CREATED = "wish_created"
    WISH_UPDATED = "wish_updated"
