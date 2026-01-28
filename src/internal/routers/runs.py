from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories import get_run
from internal.dependencies import get_session
from internal.schemas.runs import RunCreateRequest, RunLogsResponse, RunResponse
from services.runs_service import RunsService
from services.jobs import enqueue_run

router = APIRouter(prefix="/v1/runs", tags=["runs"])


@router.post("/issue", response_model=RunResponse)
async def run_issue(
    request: RunCreateRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
) -> RunResponse:
    service = RunsService()
    run = await service.create_run(session, request)
    redis = http_request.app.state.redis
    if redis:
        await enqueue_run(redis, run.id)
    return RunResponse(
        run_id=run.id,
        status=run.status,
        repo_url=run.repo_url,
        issue_number=run.issue_number or 0,
        model=run.model,
        max_iterations=run.max_iterations,
    )


@router.get("/", response_model=list[RunResponse])
async def list_runs(session: AsyncSession = Depends(get_session)) -> list[RunResponse]:
    runs = await RunsService().list_runs(session)
    return [
        RunResponse(
            run_id=run.id,
            status=run.status,
            repo_url=run.repo_url,
            issue_number=run.issue_number or 0,
            model=run.model,
            max_iterations=run.max_iterations,
        )
        for run in runs
    ]


@router.get("/{run_id}", response_model=RunResponse)
async def get_run_status(
    run_id: str, session: AsyncSession = Depends(get_session)
) -> RunResponse:
    run = await get_run(session, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunResponse(
        run_id=run.id,
        status=run.status,
        repo_url=run.repo_url,
        issue_number=run.issue_number or 0,
        model=run.model,
        max_iterations=run.max_iterations,
    )


@router.get("/{run_id}/logs", response_model=RunLogsResponse)
async def get_run_logs(
    run_id: str, session: AsyncSession = Depends(get_session)
) -> RunLogsResponse:
    run = await get_run(session, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    logs = [log.message for log in run.logs]
    return RunLogsResponse(run_id=run_id, logs=logs)
