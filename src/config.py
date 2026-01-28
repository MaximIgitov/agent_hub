from __future__ import annotations

import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="")

    database_url: str = Field(
        default_factory=lambda: env(
            "AGENT_HUB_DATABASE_URL", "sqlite+aiosqlite:///./agent_hub.db"
        )
    )
    redis_url: str = Field(
        default_factory=lambda: env("AGENT_HUB_REDIS_URL", "redis://localhost:6379/0")
    )
    openrouter_api_key: str = Field(
        default_factory=lambda: env("AGENT_HUB_OPENROUTER_API_KEY", "")
    )
    openrouter_model: str = Field(
        default_factory=lambda: env(
            "AGENT_HUB_OPENROUTER_MODEL", "google/gemini-3-flash-preview"
        )
    )
    github_webhook_secret: str = Field(
        default_factory=lambda: env("AGENT_HUB_GITHUB_WEBHOOK_SECRET", "")
    )
    app_base_url: str = Field(
        default_factory=lambda: env("AGENT_HUB_APP_BASE_URL", "http://localhost:8000")
    )
    ui_base_url: str = Field(
        default_factory=lambda: env("AGENT_HUB_UI_BASE_URL", "http://localhost:8501")
    )
    default_max_iters: int = Field(
        default_factory=lambda: int(env("AGENT_HUB_DEFAULT_MAX_ITERS", "5"))
    )
    max_patch_files: int = Field(
        default_factory=lambda: int(env("AGENT_HUB_MAX_PATCH_FILES", "20"))
    )
    max_patch_lines: int = Field(
        default_factory=lambda: int(env("AGENT_HUB_MAX_PATCH_LINES", "400"))
    )


settings = Settings()
