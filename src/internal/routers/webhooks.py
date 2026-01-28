from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from internal.dependencies import get_session
from internal.schemas.runs import RunCreateRequest
from services.jobs import enqueue_run
from services.runs_service import RunsService
from services.webhook_service import WebhookService
from config import settings

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])


@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    payload = await request.body()
    service = WebhookService()
    if not service.verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    event = request.headers.get("X-GitHub-Event", "")
    data = json.loads(payload.decode("utf-8") or "{}")
    action = data.get("action", "")
    if event == "issues" and action in {"opened", "labeled"}:
        repo_url = data.get("repository", {}).get("html_url", "")
        issue_number = data.get("issue", {}).get("number", 0)
        run = await RunsService().create_run(
            session,
            RunCreateRequest(
                repo_url=repo_url,
                issue_number=issue_number,
                model=settings.openrouter_model,
                max_iters=settings.default_max_iters,
            ),
        )
        redis = request.app.state.redis
        if redis:
            await enqueue_run(redis, run.id)
    await service.handle_event(event=event, payload=payload)
    return {"status": "ok"}
