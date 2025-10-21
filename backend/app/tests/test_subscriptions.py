from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app

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


def authenticate(client: TestClient, user_id: int, username: str) -> str:
    payload = {
        "id": user_id,
        "username": username,
        "first_name": username.title(),
    }
    init_data = build_init_data(payload)
    response = client.post("/api/auth/telegram", json={"init_data": init_data})
    assert response.status_code == 200
    return response.json()["csrf_token"]


def test_subscription_flow(client: TestClient) -> None:
    csrf_user1 = authenticate(client, 1, "follower")

    with TestClient(app) as other_client:
        authenticate(other_client, 2, "creator")

    subscribe_resp = client.post(
        "/api/subscriptions/creator",
        headers={"X-CSRF-Token": csrf_user1},
    )
    assert subscribe_resp.status_code == 201
    data = subscribe_resp.json()
    assert data["target"]["username"] == "creator"

    list_resp = client.get("/api/subscriptions")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    delete_resp = client.delete(
        "/api/subscriptions/creator",
        headers={"X-CSRF-Token": csrf_user1},
    )
    assert delete_resp.status_code == 204
