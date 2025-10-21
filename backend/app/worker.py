from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal, InvalidOperation
from html import escape

from celery import Celery
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.db import SessionLocal
from app.models.notification import Notification
from app.services import notify, telegram_bot

PRIORITY_LABELS: dict[str, str] = {
    "low": "Низкий",
    "medium": "Средний",
    "high": "Высокий",
}

STATUS_LABELS: dict[str, str] = {
    "planned": "Запланировано",
    "ordered": "Заказано",
    "gifted": "Подарено",
}

DEFAULT_NOTIFICATION_TITLE = "Желание"
DEFAULT_OWNER_LINE = "Обновления от Wishfox"


def _localize(mapping: dict[str, str], value: str | None) -> str | None:
    if not value:
        return None
    key = str(value).lower()
    return mapping.get(key, str(value))


def _format_price(value: str | None) -> str | None:
    if not value:
        return None
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return str(value)
    quantized = amount.quantize(Decimal("0.01"))
    return f"{quantized:,.2f}".replace(",", " ").replace(".", ",")


def _sanitize_tags(raw_tags: Iterable[str]) -> list[str]:
    tags: list[str] = []
    for tag in raw_tags:
        cleaned = (tag or "").strip()
        if not cleaned:
            continue
        tags.append(f"#{escape(cleaned)}")
    return tags


celery_app = Celery(
    "wishlist",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    timezone="UTC",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    beat_scheduler="celery.beat:PersistentScheduler",
)


@celery_app.task(name="notifications.send")
def send_notification(notification_id: int) -> None:
    session: Session = SessionLocal()
    try:
        notification = session.get(
            Notification,
            notification_id,
            options=(selectinload(Notification.user),),
        )
        if not notification or notification.is_sent or not notification.user:
            return
        user = notification.user
        if not user.tg_user_id:
            return

        payload = notification.payload or {}
        title = payload.get("title") or DEFAULT_NOTIFICATION_TITLE
        owner = payload.get("owner", {})
        display_name = owner.get("display_name") or ""
        deep_link = payload.get("deep_link")
        priority = payload.get("priority")
        status = payload.get("status")
        price = payload.get("price")
        url = payload.get("url")
        tags = payload.get("tags", [])
        description = payload.get("description") or ""
        wishlist = payload.get("wishlist") or {}
        wishlist_title = wishlist.get("title")

        message_lines: list[str] = []
        if display_name:
            message_lines.append(f"Обновления от <b>{escape(display_name)}</b>")
        else:
            message_lines.append(DEFAULT_OWNER_LINE)

        if wishlist_title:
            message_lines.append(f"<b>Список:</b> {escape(str(wishlist_title))}")

        safe_title = escape(str(title))
        message_lines.append(f"<b>Желание:</b> {safe_title}")

        if description:
            safe_description = escape(str(description)).replace("\n", "<br/>")
            message_lines.append(f"<b>Описание:</b> {safe_description}")

        localized_priority = _localize(PRIORITY_LABELS, priority)
        if localized_priority:
            message_lines.append(f"<b>Приоритет:</b> {escape(localized_priority)}")

        localized_status = _localize(STATUS_LABELS, status)
        if localized_status:
            message_lines.append(f"<b>Статус:</b> {escape(localized_status)}")

        formatted_price = _format_price(price)
        if formatted_price:
            message_lines.append(f"<b>Цена:</b> {formatted_price}")

        if isinstance(tags, (list, tuple, set)):
            sanitized_tags = _sanitize_tags(tags)
        else:
            sanitized_tags = []
        if sanitized_tags:
            message_lines.append("<b>Теги:</b> " + ", ".join(sanitized_tags))

        if url:
            escaped_url = escape(str(url))
            message_lines.append(f'<b>Ссылка:</b> <a href="{escaped_url}">{escaped_url}</a>')

        if deep_link:
            escaped_deep_link = escape(str(deep_link))
            message_lines.append(
                f'<b>Открыть мини-приложение:</b> <a href="{escaped_deep_link}">{escaped_deep_link}</a>'
            )

        telegram_bot.send_message(chat_id=int(user.tg_user_id), text="\n".join(message_lines))
        notify.mark_sent(session, notification)
        session.commit()
    finally:
        session.close()
