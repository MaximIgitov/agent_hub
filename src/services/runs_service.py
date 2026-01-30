from __future__ import annotations

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import EventLog, Run
from db.repositories import add_log, create_run, list_runs
from internal.schemas.runs import RunCreateRequest


class RunsService:
    async def create_run(self, session: AsyncSession, request: RunCreateRequest) -> Run:
        run = Run(
            id=str(uuid4()),
            repo_url=request.repo_url,
            issue_number=request.issue_number,
            status="NEW",
            model=request.model,
            max_iterations=request.max_iters,
        )
        run = await create_run(session, run)
        await add_log(
            session,
            EventLog(
                id=str(uuid4()),
                run_id=run.id,
                message="Run created",
                kind="run_created",
                payload={
                    "repo_url": run.repo_url,
                    "issue_number": run.issue_number,
                    "model": run.model,
                    "max_iterations": run.max_iterations,
                },
            ),
        )
        return run

    async def list_runs(self, session: AsyncSession) -> list[Run]:
        return await list_runs(session)
