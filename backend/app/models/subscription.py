from __future__ import annotations

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, IDMixin, TimestampMixin


class Subscription(Base, IDMixin, TimestampMixin):
    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("follower_id", "target_user_id", name="uq_subscription"),)

    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    target_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    follower: Mapped["User"] = relationship("User", foreign_keys=[follower_id], back_populates="following")
    target: Mapped["User"] = relationship("User", foreign_keys=[target_user_id], back_populates="followers")
