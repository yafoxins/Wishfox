from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict
from urllib.parse import parse_qsl

from fastapi import HTTPException, status

from app.config import settings


@dataclass(slots=True)
class TelegramUserPayload:
    id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    photo_url: str | None
    language_code: str | None


@dataclass(slots=True)
class TelegramAuthResult:
    user: TelegramUserPayload
    auth_date: datetime
    raw: Dict[str, Any]


class TelegramAuthError(HTTPException):
    def __init__(self, detail: str = "Invalid telegram authentication payload") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def _build_data_check_string(data: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in sorted(data.items()))


def _secret_key() -> bytes:
    return hmac.new(
        key="WebAppData".encode(),
        msg=settings.bot_token.encode(),
        digestmod=hashlib.sha256,
    ).digest()


def validate_telegram_init_data(init_data: str) -> TelegramAuthResult:
    if not init_data:
        raise TelegramAuthError("Missing initData")

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    if "hash" not in parsed:
        raise TelegramAuthError("Missing hash field")

    received_hash = parsed.pop("hash")

    data_check_string = _build_data_check_string(parsed)
    secret_key = _secret_key()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise TelegramAuthError("Hash mismatch")

    user_payload_raw = parsed.get("user")
    if not user_payload_raw:
        raise TelegramAuthError("Missing user payload")

    try:
        user_data = json.loads(user_payload_raw)
    except json.JSONDecodeError as exc:
        raise TelegramAuthError("Invalid user payload") from exc

    if not isinstance(user_data, dict) or "id" not in user_data:
        raise TelegramAuthError("User payload missing id")

    tg_user = TelegramUserPayload(
        id=int(user_data["id"]),
        username=user_data.get("username"),
        first_name=user_data.get("first_name"),
        last_name=user_data.get("last_name"),
        photo_url=user_data.get("photo_url"),
        language_code=user_data.get("language_code"),
    )

    auth_date_raw = parsed.get("auth_date")
    if not auth_date_raw:
        raise TelegramAuthError("Missing auth date")

    auth_date = datetime.fromtimestamp(int(auth_date_raw), tz=timezone.utc)
    now = datetime.now(timezone.utc)
    if abs((now - auth_date).total_seconds()) > 24 * 3600:
        raise TelegramAuthError("Auth date too old")

    return TelegramAuthResult(user=tg_user, auth_date=auth_date, raw=parsed)
