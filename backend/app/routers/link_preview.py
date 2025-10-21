from __future__ import annotations

from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import HttpUrl

from app.schemas.link_preview import LinkPreview

router = APIRouter()


class _MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._capture_title = False
        self.title: str | None = None
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_lower = tag.lower()
        if tag_lower == "title":
            self._capture_title = True
        elif tag_lower == "meta":
            attr_map = {key.lower(): (value or "") for key, value in attrs}
            name = attr_map.get("property") or attr_map.get("name")
            content = attr_map.get("content") or attr_map.get("value")
            if name and content:
                self.meta[name.lower()] = content.strip()

    def handle_data(self, data: str) -> None:
        if self._capture_title:
            text = data.strip()
            if text and not self.title:
                self.title = text

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._capture_title = False


def _extract_preview(html: str, base_url: str) -> LinkPreview:
    parser = _MetaParser()
    parser.feed(html)

    meta = parser.meta

    title = (
        meta.get("og:title")
        or meta.get("twitter:title")
        or meta.get("title")
        or parser.title
    )

    description = (
        meta.get("og:description")
        or meta.get("twitter:description")
        or meta.get("description")
    )

    image = meta.get("og:image") or meta.get("twitter:image") or meta.get("twitter:image:src")
    if image:
        image = urljoin(base_url, image)

    try:
        return LinkPreview(url=base_url, title=title, description=description, image=image)
    except Exception:
        # Validation might fail on malformed URL/image; return minimal payload
        return LinkPreview(url=base_url, title=title, description=description, image=None)


@router.get("/links/preview", response_model=LinkPreview)
def get_link_preview(url: HttpUrl = Query(..., description="Absolute URL to fetch metadata for")) -> LinkPreview:
    headers: dict[str, Any] = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/118.0 Safari/537.36"
        ),
        "Accept-Language": "ru,en;q=0.9",
    }
    target_url = str(url)
    try:
        response = httpx.get(
            target_url,
            headers=headers,
            timeout=httpx.Timeout(15.0, connect=10.0),
            follow_redirects=True,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        # If the upstream blocks us, degrade gracefully and let the client keep manual data.
        if exc.response.status_code in {400, 401, 403, 404, 410}:
            return LinkPreview(url=url)
        raise HTTPException(status_code=400, detail="Failed to fetch link preview") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=400, detail="Failed to fetch link preview") from exc

    return _extract_preview(response.text, target_url)

