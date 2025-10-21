from fastapi import APIRouter

from . import auth, debug, feed, link_preview, media, notifications, subscriptions, users, wishes, wishlists

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(wishlists.router, tags=["wishlists"])
api_router.include_router(wishes.router, tags=["wishes"])
api_router.include_router(subscriptions.router, tags=["subscriptions"])
api_router.include_router(feed.router, tags=["feed"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(debug.router, tags=["debug"])
api_router.include_router(media.router, tags=["media"])
api_router.include_router(link_preview.router, tags=["links"])
