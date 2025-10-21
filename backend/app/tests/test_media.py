from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone

from fastapi.testclient import TestClient

BOT_TOKEN = "123456:TEST"

PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGP4/5+hHgAHggJ/lRcH0QAAAABJRU5ErkJggg=="
)


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
    payload = {"id": 404, "username": "media_user"}
    response = client.post("/api/auth/telegram", json={"init_data": build_init_data(payload)})
    assert response.status_code == 200
    return response.json()["csrf_token"]


def test_upload_image(client: TestClient) -> None:
    csrf_token = authenticate(client)

    response = client.post(
        "/api/media/upload",
        headers={"X-CSRF-Token": csrf_token},
        files={"file": ("test.png", PNG_BYTES, "image/png")},
    )

    assert response.status_code == 201, response.text
    url = response.json()["url"]
    assert url.startswith("/media/")
