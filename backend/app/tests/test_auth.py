from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone

from fastapi.testclient import TestClient

BOT_TOKEN = "123456:TEST"


def build_init_data(user_payload: dict) -> str:
    auth_date = int(datetime.now(tz=timezone.utc).timestamp())
    data = {
        "auth_date": str(auth_date),
        "query_id": "AAEAAAE",
        "user": json.dumps(user_payload, separators=(",", ":")),
    }
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256).digest()
    hash_value = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    data["hash"] = hash_value
    return "&".join(f"{k}={v}" for k, v in data.items())


def test_telegram_auth_flow_success(client: TestClient) -> None:
    user_payload = {
        "id": 1111,
        "username": "wishlist_tester",
        "first_name": "Test",
        "last_name": "User",
        "photo_url": "https://example.com/avatar.png",
    }
    init_data = build_init_data(user_payload)

    response = client.post("/api/auth/telegram", json={"init_data": init_data})
    assert response.status_code == 200

    data = response.json()
    assert data["user"]["display_name"] == "Test User"
    assert data["user"]["username"] == "wishlist_tester"
    assert "csrf_token" in data
    assert "wishlist_session" in response.cookies
    assert "wishlist_csrf" in response.cookies
