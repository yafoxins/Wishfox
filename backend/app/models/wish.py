from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, IDMixin, TimestampMixin
from .enums import WishPriority, WishStatus
from .types import TagListType


class Wish(Base, IDMixin, TimestampMixin):
    __tablename__ = "wishes"

    wishlist_id: Mapped[int] = mapped_column(ForeignKey("wishlists.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    priority: Mapped[WishPriority] = mapped_column(
        Enum(
            WishPriority,
            name="wish_priority",
            values_callable=lambda e: [i.value for i in e],
        ),
        index=True,
    )
    status: Mapped[WishStatus] = mapped_column(
        Enum(
            WishStatus,
            name="wish_status",
            values_callable=lambda e: [i.value for i in e],
        ),
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, default=0, index=True)
    tags: Mapped[List[str]] = mapped_column(TagListType, default=list)

    wishlist: Mapped["Wishlist"] = relationship("Wishlist", back_populates="wishes")
