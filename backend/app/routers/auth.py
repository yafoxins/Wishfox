from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.telegram import TelegramAuthError, validate_telegram_init_data
from app.config import settings
from app.db import get_db
from app.models.user import User
from app.models.wishlist import Wishlist
from app.schemas.auth import AuthRequest, AuthResponse
from app.schemas.user import UserMe
from app.utils.security import create_csrf_token, create_session_token

router = APIRouter()


@router.post("/auth/telegram", response_model=AuthResponse)
def telegram_auth(payload: AuthRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        result = validate_telegram_init_data(payload.init_data)
    except TelegramAuthError:
        raise

    tg_user = result.user

    stmt = select(User).where(User.tg_user_id == str(tg_user.id))
    user: User | None = db.scalar(stmt)

    display_name_parts = [value for value in [tg_user.first_name, tg_user.last_name] if value]
    display_name = " ".join(display_name_parts).strip() or tg_user.username or "Wishlist User"

    if user is None:
        try:
            user = User(
                tg_user_id=str(tg_user.id),
                tg_username=tg_user.username,
                display_name=display_name,
                avatar_url=tg_user.photo_url,
                locale=tg_user.language_code or "en",
            )
            db.add(user)
            db.flush()
            wishlist = Wishlist(owner_id=user.id, title=f"{user.display_name}'s wishlist")
            db.add(wishlist)
        except IntegrityError:
            db.rollback()
            user = db.scalar(select(User).where(User.tg_user_id == str(tg_user.id)))
    else:
        user.tg_username = tg_user.username or user.tg_username
        user.avatar_url = tg_user.photo_url or user.avatar_url
        if not user.display_name:
            user.display_name = display_name
        user.locale = tg_user.language_code or user.locale

    db.commit()
    user = db.get(User, user.id)

    session_token = create_session_token(user.id)
    csrf_token = create_csrf_token(session_token)

    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_token,
        httponly=True,
        secure=settings.is_prod,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 30,
    )
    response.set_cookie(
        key=settings.csrf_cookie_name,
        value=csrf_token,
        httponly=False,
        secure=settings.is_prod,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 30,
    )

    return AuthResponse(user=UserMe.model_validate(user), csrf_token=csrf_token)
