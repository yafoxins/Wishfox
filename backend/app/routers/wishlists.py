from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models.enums import WishlistVisibility
from app.models.user import User
from app.models.wishlist import Wishlist
from app.schemas.wishlist import WishlistCreate, WishlistDetail, WishlistRead
from app.utils.security import csrf_protect, get_current_user, get_optional_user

router = APIRouter()


@router.get("/wishlists/mine", response_model=list[WishlistDetail])
def get_my_wishlists(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[WishlistDetail]:
    stmt = (
        select(Wishlist)
        .where(Wishlist.owner_id == current_user.id)
        .options(selectinload(Wishlist.wishes))
    )
    wishlists = db.scalars(stmt).all()
    return [WishlistDetail.model_validate(item) for item in wishlists]


@router.post(
    "/wishlists",
    response_model=WishlistRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
def create_wishlist(
    wishlist: WishlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WishlistRead:
    new_wishlist = Wishlist(
        owner_id=current_user.id,
        title=wishlist.title,
        visibility=wishlist.visibility,
        cover_url=wishlist.cover_url,
    )
    db.add(new_wishlist)
    db.commit()
    db.refresh(new_wishlist)
    return WishlistRead.model_validate(new_wishlist)


@router.get("/users/{username}/wishlist", response_model=WishlistDetail)
def get_user_wishlist(
    username: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> WishlistDetail:
    try:
        user_id = int(username)
    except ValueError:
        lowered = username.lower()
        user_stmt = select(User).where(
            (func.lower(User.tg_username) == lowered) | (func.lower(User.custom_username) == lowered)
        )
        target_user = db.scalar(user_stmt)
    else:
        target_user = db.get(User, user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    wishlist_stmt = (
        select(Wishlist)
        .where(Wishlist.owner_id == target_user.id)
        .options(selectinload(Wishlist.wishes))
    )
    wishlist = db.scalar(wishlist_stmt)
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    if wishlist.visibility == WishlistVisibility.PRIVATE and (
        not current_user or current_user.id != target_user.id
    ):
        raise HTTPException(status_code=403, detail="Wishlist is private")

    return WishlistDetail.model_validate(wishlist)
