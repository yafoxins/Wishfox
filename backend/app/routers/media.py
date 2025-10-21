from __future__ import annotations

import imghdr
import os
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import settings
from app.models.user import User
from app.utils.security import csrf_protect, get_current_user

ALLOWED_EXTENSIONS: set[str] = {"jpg", "jpeg", "png", "gif", "webp"}

router = APIRouter(prefix="/media")


def _validate_extension(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image format")
    return ext


async def _read_file(upload_file: UploadFile) -> bytes:
    data = await upload_file.read()
    max_bytes = settings.media_max_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")
    return data


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def upload_image(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user),
) -> dict[Literal["url"], str]:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File has no name")

    _ = _validate_extension(file.filename)
    data = await _read_file(file)
    detected = imghdr.what(None, data)
    if not detected:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image content")
    mapped = "jpg" if detected == "jpeg" else detected
    if mapped not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image content")

    target_dir = Path(settings.media_root)
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}.{mapped}"
    destination = target_dir / filename
    destination.write_bytes(data)

    if os.name != "nt":
        os.chmod(destination, 0o644)

    url = f"{settings.media_base_url}/{filename}"
    return {"url": url}
