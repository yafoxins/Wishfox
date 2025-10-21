from __future__ import annotations

from enum import Enum

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from .base import Base, IDMixin, TimestampMixin


class EventAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class EventEntity(str, Enum):
    WISH = "wish"


class Event(Base, IDMixin, TimestampMixin):
    __tablename__ = "events"

    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    entity: Mapped[EventEntity] = mapped_column(
        SAEnum(EventEntity, name="event_entity", values_callable=lambda e: [i.value for i in e])
    )
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[EventAction] = mapped_column(
        SAEnum(EventAction, name="event_action", values_callable=lambda e: [i.value for i in e])
    )
    diff: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=True)
