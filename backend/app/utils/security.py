from __future__ import annotations

import hashlib
import hmac
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Request, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User

SESSION_SALT = "wishlist-session"
CSRF_SALT = "wishlist-csrf"


def _session_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.secret_key, salt=SESSION_SALT)


def create_session_token(user_id: int) -> str:
    serializer = _session_serializer()
    return serializer.dumps({"user_id": user_id})


def verify_session_token(token: str, max_age: int = 60 * 60 * 24 * 30) -> int:
    serializer = _session_serializer()
    try:
        data = serializer.loads(token, max_age=max_age)
    except SignatureExpired as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired") from exc
    except BadSignature as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session") from exc

    user_id = data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session payload")
    return int(user_id)


def create_csrf_token(session_token: str) -> str:
    digest = hmac.new(
        key=settings.csrf_secret.encode(),
        msg=f"{CSRF_SALT}:{session_token}".encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return digest


def validate_csrf_token(session_token: str, csrf_token: str) -> bool:
    expected = create_csrf_token(session_token)
    return hmac.compare_digest(expected, csrf_token)


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    session_token: Optional[str] = Cookie(None, alias=settings.session_cookie_name),
) -> User:
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user_id = verify_session_token(session_token)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    request.state.session_token = session_token
    request.state.user = user
    return user


def get_optional_user(
    request: Request,
    db: Session = Depends(get_db),
    session_token: Optional[str] = Cookie(None, alias=settings.session_cookie_name),
) -> User | None:
    if not session_token:
        return None
    try:
        user_id = verify_session_token(session_token)
    except HTTPException:
        return None
    user = db.get(User, user_id)
    if user:
        request.state.session_token = session_token
        request.state.user = user
    return user


def csrf_protect(request: Request) -> None:
    # Dependency execution order may call this before get_current_user.
    # Fallback to cookie when request.state.session_token not set.
    session_token = getattr(request.state, "session_token", None)
    if not session_token:
        session_token = request.cookies.get(settings.session_cookie_name)
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    header_token = request.headers.get(settings.csrf_header_name)
    cookie_token = request.cookies.get(settings.csrf_cookie_name)

    if not header_token or not cookie_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing CSRF token")

    if not (validate_csrf_token(session_token, header_token) and header_token == cookie_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")
