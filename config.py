from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENT_HUB_")

    database_url: str = Field(default="sqlite+aiosqlite:///./agent_hub.db")
    redis_url: str = Field(default="redis://localhost:6379/0")
    openrouter_api_key: str = Field(default="")
    openrouter_model: str = Field(default="google/gemini-3-flash-preview")
    github_webhook_secret: str = Field(default="")
    app_base_url: str = Field(default="http://localhost:8000")
    default_max_iters: int = Field(default=5)
    max_patch_files: int = Field(default=20)
    max_patch_lines: int = Field(default=400)


settings = Settings()
