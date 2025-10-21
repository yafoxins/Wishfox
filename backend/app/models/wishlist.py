from __future__ import annotations

from typing import List

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, IDMixin, TimestampMixin
from .enums import WishlistVisibility


class Wishlist(Base, IDMixin, TimestampMixin):
    __tablename__ = "wishlists"

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    visibility: Mapped[WishlistVisibility] = mapped_column(
        Enum(
            WishlistVisibility,
            name="wishlist_visibility",
            values_callable=lambda e: [i.value for i in e],
        ),
        server_default=WishlistVisibility.PUBLIC.value,
    )
    cover_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    owner: Mapped["User"] = relationship("User", back_populates="wishlists")
    wishes: Mapped[List["Wish"]] = relationship(
        "Wish", back_populates="wishlist", cascade="all, delete-orphan", order_by="Wish.position"
    )
