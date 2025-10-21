from __future__ import annotations

from pydantic import AnyHttpUrl, BaseModel, HttpUrl


class LinkPreview(BaseModel):
    url: HttpUrl
    title: str | None = None
    description: str | None = None
    image: AnyHttpUrl | None = None
