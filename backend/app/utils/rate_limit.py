from __future__ import annotations

from fastapi import HTTPException, Request, status

from app.utils.redis import get_redis


def rate_limit(scope: str, limit: int = 30, window: int = 60):
    def dependency(request: Request) -> None:
        redis = get_redis()
        user = getattr(request.state, "user", None)
        identifier = getattr(user, "id", None) or request.client.host or "anonymous"
        key = f"rl:{scope}:{identifier}"
        current = redis.incr(key)
        if current == 1:
            redis.expire(key, window)
        if current > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please slow down.",
            )

    return dependency
