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


def authenticate(client: TestClient) -> str:
    payload = {"id": 42, "username": "notify_user", "first_name": "Notify"}
    init_data = build_init_data(payload)
    response = client.post("/api/auth/telegram", json={"init_data": init_data})
    assert response.status_code == 200
    return response.json()["csrf_token"]


def test_trigger_notification(client: TestClient) -> None:
    csrf_token = authenticate(client)
    response = client.post("/api/notifications/test", headers={"X-CSRF-Token": csrf_token})
    assert response.status_code == 202
    assert response.json()["detail"] == "Notification scheduled"
