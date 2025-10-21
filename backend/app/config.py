from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="",
    )

    env: str = "development"
    secret_key: str
    csrf_secret: str
    bot_token: str
    telegram_bot_name: str = "wishlist_bot"

    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "wishlist"
    postgres_user: str = "wishlist"
    postgres_password: str = "wishlist"

    redis_url: str = "redis://redis:6379/0"

    backend_url: AnyHttpUrl = "http://localhost/api"
    frontend_url: AnyHttpUrl = "http://localhost:5173"

    allowed_origins_raw: str = "http://localhost:5173"

    notify_batch_seconds: int = 30

    session_cookie_name: str = "wishlist_session"
    csrf_cookie_name: str = "wishlist_csrf"
    csrf_header_name: str = "X-CSRF-Token"
    media_root: str = "/app/media"
    media_base_url: str = "/media"
    media_max_mb: int = 5

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]

    @property
    def is_prod(self) -> bool:
        return self.env.lower() in {"prod", "production"}


@lru_cache(1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]


settings = get_settings()
