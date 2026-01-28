from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from services.orchestrator import Orchestrator
from services.runs_service import RunsService
from services.webhook_service import WebhookService


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    sessionmaker = request.app.state.db_sessionmaker
    async with sessionmaker() as session:
        yield session


def get_orchestrator() -> Orchestrator:
    return Orchestrator()


def get_runs_service() -> RunsService:
    return RunsService()


def get_webhook_service() -> WebhookService:
    return WebhookService()
