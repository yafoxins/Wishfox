from __future__ import annotations

from decimal import Decimal
from typing import List
from enum import Enum as PyEnum

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models.enums import NotificationType, WishPriority, WishStatus, WishlistVisibility
from app.models.user import User
from app.models.wish import Wish
from app.models.wishlist import Wishlist
from app.schemas.common import Paginated
from app.schemas.wish import WishCreate, WishRead, WishReorderItem, WishUpdate
from app.services import notify
from app.utils.rate_limit import rate_limit
from app.utils.security import csrf_protect, get_current_user
from app.worker import send_notification

router = APIRouter(prefix="/wishes")


def _base_query(owner_id: int):
    return select(Wish).join(Wishlist).where(Wishlist.owner_id == owner_id)


@router.get("", response_model=Paginated[WishRead])
def list_wishes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    q: str | None = Query(None, max_length=255),
    priority: WishPriority | None = Query(None),
    status: WishStatus | None = Query(None),
    tags: List[str] | None = Query(None),
    price_min: Decimal | None = Query(None),
    price_max: Decimal | None = Query(None),
    sort: str = Query("created_at"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> Paginated[WishRead]:
    query = _base_query(current_user.id).options(selectinload(Wish.wishlist))

    if q:
        like = f"%{q.lower()}%"
        query = query.where(func.lower(Wish.title).like(like) | func.lower(Wish.description).like(like))
    if priority:
        query = query.where(Wish.priority == priority)
    if status:
        query = query.where(Wish.status == status)
    if tags:
        for tag in tags:
            query = query.where(Wish.tags.contains([tag]))
    if price_min is not None:
        query = query.where(Wish.price >= price_min)
    if price_max is not None:
        query = query.where(Wish.price <= price_max)

    sort_map = {
        "created_at": Wish.created_at.desc(),
        "priority": Wish.priority.desc(),
        "price": Wish.price.asc(),
        "position": Wish.position.asc(),
        "updated_at": Wish.updated_at.desc(),
    }
    order_by = sort_map.get(sort, Wish.created_at.desc())
    query = query.order_by(order_by)

    count_query = query.with_only_columns(func.count()).order_by(None)
    total = db.scalar(count_query) or 0
    items = db.scalars(query.offset((page - 1) * per_page).limit(per_page)).all()
    return {
        "items": [WishRead.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.post(
    "",
    response_model=WishRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect), Depends(rate_limit("wish:create", limit=20, window=60))],
)
def create_wish(
    payload: WishCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WishRead:
    wishlist = db.get(Wishlist, payload.wishlist_id)
    if not wishlist or wishlist.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    max_position = db.scalar(
        select(func.max(Wish.position)).where(Wish.wishlist_id == payload.wishlist_id)
    )
    position = (max_position or 0) + 1

    wish = Wish(
        wishlist_id=payload.wishlist_id,
        title=payload.title,
        description=payload.description,
        url=payload.url,
        price=payload.price,
        image_url=payload.image_url,
        priority=payload.priority,
        status=payload.status,
        tags=payload.tags,
        position=position,
    )
    wish.wishlist = wishlist
    db.add(wish)
    db.flush()

    notifications = []
    if wishlist.visibility in {WishlistVisibility.PUBLIC, WishlistVisibility.UNLISTED}:
        notifications = notify.create_notifications(db, wish, NotificationType.WISH_CREATED)

    db.commit()
    db.refresh(wish)

    for notification in notifications:
        send_notification.delay(notification.id)

    return WishRead.model_validate(wish)


@router.patch(
    "/{wish_id}",
    response_model=WishRead,
    dependencies=[Depends(csrf_protect), Depends(rate_limit("wish:update", limit=30, window=60))],
)
def update_wish(
    wish_id: int,
    payload: WishUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WishRead:
    wish = db.get(Wish, wish_id)
    if not wish or wish.wishlist.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Wish not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if isinstance(value, PyEnum):
            value = value.value
        setattr(wish, field, value)

    notifications = []
    if wish.wishlist.visibility in {WishlistVisibility.PUBLIC, WishlistVisibility.UNLISTED}:
        notifications = notify.create_notifications(db, wish, NotificationType.WISH_UPDATED)

    db.add(wish)
    db.commit()
    db.refresh(wish)

    for notification in notifications:
        send_notification.delay(notification.id)

    return WishRead.model_validate(wish)


@router.delete(
    "/{wish_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(csrf_protect), Depends(rate_limit("wish:delete", limit=20, window=60))],
)
def delete_wish(
    wish_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    wish = db.get(Wish, wish_id)
    if not wish or wish.wishlist.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Wish not found")
    db.delete(wish)
    db.commit()


@router.post(
    "/reorder",
    dependencies=[Depends(csrf_protect), Depends(rate_limit("wish:reorder", limit=10, window=60))],
)
def reorder_wishes(
    items: List[WishReorderItem],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    wish_ids = [item.id for item in items]
    wishes_stmt = (
        select(Wish)
        .join(Wishlist)
        .where(Wish.id.in_(wish_ids), Wishlist.owner_id == current_user.id)
    )
    wishes = db.scalars(wishes_stmt).all()
    wishes_map = {wish.id: wish for wish in wishes}
    for item in items:
        wish = wishes_map.get(item.id)
        if not wish:
            continue
        wish.position = item.position
        db.add(wish)
    db.commit()
    return {"detail": "Reordered"}
