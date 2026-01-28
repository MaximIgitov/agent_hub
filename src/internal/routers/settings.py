from __future__ import annotations

from fastapi import APIRouter

from config import settings
from internal.schemas.settings import LimitsSettingsRequest, ModelSettingsRequest

router = APIRouter(prefix="/v1/settings", tags=["settings"])


@router.post("/model")
async def set_model(request: ModelSettingsRequest) -> dict[str, str]:
    settings.openrouter_model = request.model
    return {"model": settings.openrouter_model}


@router.post("/limits")
async def set_limits(request: LimitsSettingsRequest) -> dict[str, int]:
    settings.default_max_iters = request.max_iters
    return {"max_iters": settings.default_max_iters}
