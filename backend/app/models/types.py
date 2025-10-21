from __future__ import annotations

from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON, TypeDecorator


class TagListType(TypeDecorator):
    """JSON-backed list of strings with postgres optimisation."""

    impl = JSON
    cache_ok = True

    def process_bind_param(self, value: Any, dialect) -> Any:
        if value is None:
            return []
        return value

    def process_result_value(self, value: Any, dialect) -> Any:
        if value is None:
            return []
        return value

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())
