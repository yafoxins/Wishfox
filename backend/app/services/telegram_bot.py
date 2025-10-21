from __future__ import annotations

import json
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

API_BASE = f"https://api.telegram.org/bot{settings.bot_token}"


class TelegramBotError(Exception):
    pass


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
def send_message(chat_id: int, text: str, reply_markup: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    with httpx.Client(timeout=10.0) as client:
        response = client.post(f"{API_BASE}/sendMessage", data=payload)
        if response.status_code >= 400:
            raise TelegramBotError(f"Telegram API error: {response.status_code} {response.text}")
        data = response.json()
        if not data.get("ok"):
            raise TelegramBotError(f"Telegram API failure: {data}")
        return data
