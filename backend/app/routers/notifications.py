from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.enums import NotificationType
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationRead
from app.utils.security import csrf_protect, get_current_user
from app.worker import send_notification

router = APIRouter(prefix="/notifications")


@router.get("", response_model=list[NotificationRead])
def list_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[NotificationRead]:
    stmt = select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc())
    notifications = db.scalars(stmt).all()
    return [NotificationRead.model_validate(item) for item in notifications]


@router.post(
    "/test",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(csrf_protect)],
)
def trigger_test_notification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    payload = {
        "title": "Demo wish",
        "priority": "medium",
        "owner": {"id": current_user.id, "display_name": current_user.display_name, "username": current_user.tg_username or current_user.custom_username},
        "deep_link": None,
    }
    notification = Notification(user_id=current_user.id, type=NotificationType.WISH_CREATED, payload=payload)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    send_notification.delay(notification.id)
    return {"detail": "Notification scheduled"}
