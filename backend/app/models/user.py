from __future__ import annotations

from typing import List, Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, IDMixin, TimestampMixin


class User(Base, IDMixin, TimestampMixin):
    __tablename__ = "users"

    tg_user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    tg_username: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    custom_username: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    display_name: Mapped[str] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    locale: Mapped[str] = mapped_column(String(8), default="en")

    wishlists: Mapped[List["Wishlist"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    following: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        foreign_keys="Subscription.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )
    followers: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        foreign_keys="Subscription.target_user_id",
        back_populates="target",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
