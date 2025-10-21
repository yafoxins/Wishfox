from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from decimal import Decimal

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


def authenticate(client: TestClient, user_id: int = 1, username: str = "wishlist_owner") -> str:
    payload = {
        "id": user_id,
        "username": username,
        "first_name": "Owner",
        "last_name": "User",
    }
    init_data = build_init_data(payload)
    response = client.post("/api/auth/telegram", json={"init_data": init_data})
    assert response.status_code == 200
    csrf_token = response.json()["csrf_token"]
    return csrf_token


def test_wish_crud_flow(client: TestClient) -> None:
    csrf_token = authenticate(client)

    wishlists_response = client.get("/api/wishlists/mine")
    assert wishlists_response.status_code == 200
    wishlists = wishlists_response.json()
    assert wishlists
    wishlist_id = wishlists[0]["id"]

    create_payload = {
        "wishlist_id": wishlist_id,
        "title": "New Camera",
        "description": "Mirrorless camera for travel",
        "url": "https://example.com/camera",
        "price": str(Decimal("999.99")),
        "priority": "high",
        "status": "planned",
        "tags": ["tech", "travel"],
    }

    create_response = client.post(
        "/api/wishes",
        json=create_payload,
        headers={"X-CSRF-Token": csrf_token},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "New Camera"
    wish_id = created["id"]

    list_response = client.get("/api/wishes")
    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == wish_id

    update_response = client.patch(
        f"/api/wishes/{wish_id}",
        json={"status": "ordered"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "ordered"

    delete_response = client.delete(
        f"/api/wishes/{wish_id}",
        headers={"X-CSRF-Token": csrf_token},
    )
    assert delete_response.status_code == 204

    list_response_after = client.get("/api/wishes")
    assert list_response_after.status_code == 200
    assert list_response_after.json()["total"] == 0
