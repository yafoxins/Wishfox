"""Initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2025-10-19
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

ENUM_DEFINITIONS = {
    "wishlist_visibility": ("public", "unlisted", "private"),
    "wish_priority": ("low", "medium", "high"),
    "wish_status": ("planned", "ordered", "gifted"),
    "notification_type": ("wish_created", "wish_updated"),
    "event_entity": ("wish",),
    "event_action": ("create", "update", "delete"),
}


def _prepare_enum(name: str, values: tuple[str, ...]) -> postgresql.ENUM:
    op.execute(sa.text(f"DROP TYPE IF EXISTS {name} CASCADE"))
    values_sql = ", ".join(f"'{value}'" for value in values)
    op.execute(sa.text(f"CREATE TYPE {name} AS ENUM ({values_sql})"))
    return postgresql.ENUM(*values, name=name, create_type=False)


def upgrade() -> None:
    enums = {name: _prepare_enum(name, values) for name, values in ENUM_DEFINITIONS.items()}

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tg_user_id", sa.String(length=64), nullable=False),
        sa.Column("tg_username", sa.String(length=255), nullable=True),
        sa.Column("custom_username", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("locale", sa.String(length=8), nullable=False, server_default="en"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"])
    op.create_index(op.f("ix_users_tg_user_id"), "users", ["tg_user_id"], unique=True)
    op.create_index("ix_users_tg_username", "users", ["tg_username"], unique=True)
    op.create_index("ix_users_custom_username", "users", ["custom_username"], unique=True)

    op.create_table(
        "wishlists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("visibility", enums["wishlist_visibility"], nullable=False, server_default="public"),
        sa.Column("cover_url", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_wishlists_id"), "wishlists", ["id"])

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("follower_id", sa.Integer(), nullable=False),
        sa.Column("target_user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["follower_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("follower_id", "target_user_id", name="uq_subscription"),
    )
    op.create_index(op.f("ix_subscriptions_id"), "subscriptions", ["id"])

    op.create_table(
        "wishes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("wishlist_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url", sa.String(length=512), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("image_url", sa.String(length=512), nullable=True),
        sa.Column("priority", enums["wish_priority"], nullable=False, server_default="medium"),
        sa.Column("status", enums["wish_status"], nullable=False, server_default="planned"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["wishlist_id"], ["wishlists.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_wishes_id"), "wishes", ["id"])
    op.create_index(op.f("ix_wishes_wishlist_id"), "wishes", ["wishlist_id"])
    op.create_index(op.f("ix_wishes_priority"), "wishes", ["priority"])
    op.create_index(op.f("ix_wishes_status"), "wishes", ["status"])
    op.create_index(op.f("ix_wishes_position"), "wishes", ["position"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", enums["notification_type"], nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("is_sent", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"])
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"])
    op.create_index(op.f("ix_notifications_type"), "notifications", ["type"])

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("entity", enums["event_entity"], nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("action", enums["event_action"], nullable=False),
        sa.Column("diff", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_id"), "events", ["id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_events_id"), table_name="events")
    op.drop_table("events")

    op.drop_index(op.f("ix_notifications_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    op.drop_table("notifications")

    op.drop_index(op.f("ix_wishes_position"), table_name="wishes")
    op.drop_index(op.f("ix_wishes_status"), table_name="wishes")
    op.drop_index(op.f("ix_wishes_priority"), table_name="wishes")
    op.drop_index(op.f("ix_wishes_wishlist_id"), table_name="wishes")
    op.drop_index(op.f("ix_wishes_id"), table_name="wishes")
    op.drop_table("wishes")

    op.drop_index(op.f("ix_subscriptions_id"), table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index(op.f("ix_wishlists_id"), table_name="wishlists")
    op.drop_table("wishlists")

    op.drop_index("ix_users_custom_username", table_name="users")
    op.drop_index("ix_users_tg_username", table_name="users")
    op.drop_index(op.f("ix_users_tg_user_id"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")

    for enum_name in ENUM_DEFINITIONS:
        op.execute(sa.text(f"DROP TYPE IF EXISTS {enum_name} CASCADE"))
