from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select

from app.db import session_scope
from app.models.enums import WishPriority, WishStatus, WishlistVisibility
from app.models.subscription import Subscription
from app.models.user import User
from app.models.wish import Wish
from app.models.wishlist import Wishlist


def _user_exists(session) -> bool:
  return session.scalar(select(User.id).limit(1)) is not None


def seed() -> None:
  with session_scope() as session:
    if _user_exists(session):
      return

    users = [
      User(
        tg_user_id="1001",
        tg_username="alice",
        display_name="Alice Dreamer",
        avatar_url=None,
        bio="Curating pleasant surprises.",
      ),
      User(
        tg_user_id="1002",
        tg_username="bob",
        display_name="Bob Explorer",
        avatar_url=None,
        bio="Always ready for the next adventure.",
      ),
      User(
        tg_user_id="1003",
        tg_username="carol",
        display_name="Carol Maker",
        avatar_url=None,
        bio="Designing cozy corners and warm vibes.",
      ),
    ]
    session.add_all(users)
    session.flush()

    wishlist_titles = [
      "Festive Season Wishes",
      "Tech & Travel Gear",
      "Slow Living Essentials",
    ]

    wish_samples = [
      [
        ("Handmade ceramic mugs", WishPriority.MEDIUM, WishStatus.PLANNED, Decimal("35.00"), ["home", "tea"]),
        ("Wool throw blanket", WishPriority.HIGH, WishStatus.PLANNED, Decimal("120.00"), ["cozy", "winter"]),
        ("Scented candle set", WishPriority.LOW, WishStatus.GIFTED, Decimal("48.00"), ["home", "relax"]),
      ],
      [
        ("Mirrorless camera strap", WishPriority.MEDIUM, WishStatus.PLANNED, Decimal("55.00"), ["travel", "photo"]),
        ("Packing cubes trio", WishPriority.LOW, WishStatus.ORDERED, Decimal("30.00"), ["travel"]),
        ("Noise cancelling earbuds", WishPriority.HIGH, WishStatus.PLANNED, Decimal("180.00"), ["tech", "music"]),
      ],
      [
        ("Indoor herb garden kit", WishPriority.HIGH, WishStatus.PLANNED, Decimal("65.00"), ["home", "kitchen"]),
        ("Cozy reading lamp", WishPriority.MEDIUM, WishStatus.PLANNED, Decimal("90.00"), ["home", "decor"]),
        ("Mindful journal", WishPriority.LOW, WishStatus.PLANNED, Decimal("24.00"), ["wellness", "writing"]),
      ],
    ]

    wishlists = []
    for user, title, wishes in zip(users, wishlist_titles, wish_samples, strict=True):
      wishlist = Wishlist(owner_id=user.id, title=title, visibility=WishlistVisibility.PUBLIC)
      session.add(wishlist)
      session.flush()
      wishlists.append(wishlist)

      for index, (wish_title, priority, status, price, tags) in enumerate(wishes):
        session.add(
          Wish(
            wishlist_id=wishlist.id,
            title=wish_title,
            description=None,
            price=price,
            priority=priority,
            status=status,
            position=index,
            tags=tags,
          )
        )

    # Bob follows Alice
    session.add(Subscription(follower_id=users[1].id, target_user_id=users[0].id))
    # Carol follows Bob
    session.add(Subscription(follower_id=users[2].id, target_user_id=users[1].id))


if __name__ == "__main__":
  seed()
