from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models.enums import NotificationType
from app.models.notification import Notification
from app.models.subscription import Subscription
from app.models.user import User
from app.models.wish import Wish


def _wish_payload(wish: Wish) -> dict:
    wishlist = wish.wishlist
    owner = wishlist.owner if wishlist else None
    username = owner.tg_username or owner.custom_username if owner else ""
    deep_link = f"https://t.me/{settings.telegram_bot_name}?startapp={username}" if username else None

    def _enum_or_str(value):
        try:
            return value.value  # type: ignore[attr-defined]
        except Exception:
            return str(value) if value is not None else None

    return {
        "wish_id": wish.id,
        "title": wish.title,
        "description": wish.description,
        "url": wish.url,
        "price": str(wish.price) if wish.price is not None else None,
        "tags": list(wish.tags or []),
        "priority": _enum_or_str(wish.priority),
        "status": _enum_or_str(wish.status),
        "owner": {
            "id": owner.id if owner else None,
            "display_name": owner.display_name if owner else "",
            "username": username,
        },
        "wishlist": {
            "id": wishlist.id if wishlist else None,
            "title": wishlist.title if wishlist else "",
            "visibility": wishlist.visibility.value if wishlist else "",
        },
        "deep_link": deep_link,
        "image_url": wish.image_url,
    }


def create_notifications(session: Session, wish: Wish, notification_type: NotificationType) -> List[Notification]:
    owner: User = wish.wishlist.owner  # type: ignore[assignment]
    followers_stmt = (
        select(Subscription)
        .where(Subscription.target_user_id == owner.id)
        .join(User, User.id == Subscription.follower_id)
    )
    subscriptions: Iterable[Subscription] = session.scalars(followers_stmt).all()
    notifications: List[Notification] = []
    payload = _wish_payload(wish)
    for sub in subscriptions:
        notification = Notification(
            user_id=sub.follower_id,
            type=notification_type.value,
            payload=payload,
            is_sent=False,
        )
        session.add(notification)
        notifications.append(notification)
    return notifications


def mark_sent(session: Session, notification: Notification) -> None:
    notification.is_sent = True
    notification.sent_at = datetime.now(timezone.utc)
    session.add(notification)
