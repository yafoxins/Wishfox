from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models.enums import WishlistVisibility
from app.models.subscription import Subscription
from app.models.user import User
from app.models.wishlist import Wishlist
from app.schemas.subscription import SubscriptionRead
from app.utils.rate_limit import rate_limit
from app.utils.security import csrf_protect, get_current_user

router = APIRouter(prefix="/subscriptions")


def _find_user(db: Session, username: str) -> User | None:
    try:
        user_id = int(username)
    except ValueError:
        lowered = username.lower()
        stmt = select(User).where(
            (func.lower(User.tg_username) == lowered) | (func.lower(User.custom_username) == lowered)
        )
        return db.scalar(stmt)
    return db.get(User, user_id)


@router.get("", response_model=list[SubscriptionRead])
def list_subscriptions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[SubscriptionRead]:
    stmt = (
        select(Subscription)
        .options(selectinload(Subscription.target))
        .where(Subscription.follower_id == current_user.id)
    )
    subscriptions = db.scalars(stmt).all()
    return [SubscriptionRead.model_validate(item) for item in subscriptions]


@router.post(
    "/{username}",
    response_model=SubscriptionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect), Depends(rate_limit("subscription:create", limit=10, window=60))],
)
def subscribe(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubscriptionRead:
    target_user = _find_user(db, username)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot subscribe to yourself")

    wishlist_stmt = select(Wishlist).where(Wishlist.owner_id == target_user.id)
    wishlist = db.scalar(wishlist_stmt)
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")
    if wishlist.visibility == WishlistVisibility.PRIVATE:
        raise HTTPException(status_code=403, detail="Wishlist is private")

    existing = db.scalar(
        select(Subscription).where(
            Subscription.follower_id == current_user.id,
            Subscription.target_user_id == target_user.id,
        )
    )
    if existing:
        return SubscriptionRead.model_validate(existing)

    subscription = Subscription(follower_id=current_user.id, target_user_id=target_user.id)
    db.add(subscription)
    db.commit()
    subscription = db.get(
        Subscription,
        subscription.id,
        options=(selectinload(Subscription.target),),
    )
    if not subscription:
        raise HTTPException(status_code=500, detail="Subscription creation failed")
    return SubscriptionRead.model_validate(subscription)


@router.delete(
    "/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(csrf_protect)],
)
def unsubscribe(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    target_user = _find_user(db, username)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    subscription = db.scalar(
        select(Subscription).where(
            Subscription.follower_id == current_user.id,
            Subscription.target_user_id == target_user.id,
        )
    )
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    db.delete(subscription)
    db.commit()
