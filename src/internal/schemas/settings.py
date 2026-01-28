from __future__ import annotations

from pydantic import BaseModel


class ModelSettingsRequest(BaseModel):
    model: str


class LimitsSettingsRequest(BaseModel):
    max_iters: int
