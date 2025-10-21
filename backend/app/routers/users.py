from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.user import UserMe, UserPublic, UserUpdateRequest
from app.utils.security import csrf_protect, get_current_user

router = APIRouter()


@router.get("/me", response_model=UserMe)
def read_me(current_user: User = Depends(get_current_user)) -> UserMe:
    return UserMe.model_validate(current_user)


@router.patch("/me", response_model=UserMe, dependencies=[Depends(csrf_protect)])
def update_me(
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserMe:
    if payload.custom_username:
        if current_user.tg_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom username is only allowed when Telegram username is missing.",
            )
        custom_username = payload.custom_username.lower()
        exists_stmt = (
            select(User)
            .where(User.custom_username == custom_username)
            .where(User.id != current_user.id)
        )
        if db.scalar(exists_stmt):
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.custom_username = custom_username

    if payload.display_name is not None:
        current_user.display_name = payload.display_name
    if payload.bio is not None:
        current_user.bio = payload.bio
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
    if payload.locale is not None:
        current_user.locale = payload.locale

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserMe.model_validate(current_user)


def _resolve_user(db: Session, identifier: str) -> User | None:
    try:
        user_id = int(identifier)
    except ValueError:
        lowered = identifier.lower()
        stmt = select(User).where(
            or_(
                func.lower(User.tg_username) == lowered,
                func.lower(User.custom_username) == lowered,
            )
        )
        return db.scalar(stmt)
    return db.get(User, user_id)


@router.get("/users/{username}", response_model=UserPublic)
def get_user_public(username: str, db: Session = Depends(get_db)) -> UserPublic:
    user = _resolve_user(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublic.model_validate(user)
