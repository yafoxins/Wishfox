from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models.enums import WishlistVisibility
from app.models.subscription import Subscription
from app.models.user import User
from app.models.wish import Wish
from app.models.wishlist import Wishlist
from app.schemas.feed import FeedItem
from app.schemas.user import UserPublic
from app.schemas.wish import WishRead
from app.utils.security import get_current_user

router = APIRouter(prefix="/feed")


@router.get("", response_model=list[FeedItem])
def fetch_feed(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[FeedItem]:
    # Build feed via two-step approach: fetch subscriptions first, then public wishes of targets
    subscriptions_stmt = select(Subscription).where(Subscription.follower_id == current_user.id)
    subscriptions = db.scalars(subscriptions_stmt).all()
    target_ids = [sub.target_user_id for sub in subscriptions]
    if not target_ids:
        return []

    wishes_stmt = (
        select(Wish)
        .join(Wishlist)
        .options(selectinload(Wish.wishlist).selectinload(Wishlist.owner))
        .where(
            Wishlist.owner_id.in_(target_ids),
            Wishlist.visibility != WishlistVisibility.PRIVATE,
        )
        .order_by(Wish.updated_at.desc())
        .limit(50)
    )
    wishes = db.scalars(wishes_stmt).all()

    feed: list[FeedItem] = []
    for wish in wishes:
        wishlist = wish.wishlist
        owner = wishlist.owner if wishlist else None
        if not owner:
            continue
        feed.append(
            FeedItem(
                actor=UserPublic.model_validate(owner),
                wish=WishRead.model_validate(wish),
                action="created" if wish.created_at == wish.updated_at else "updated",
                created_at=wish.updated_at,
            )
        )
    return feed
