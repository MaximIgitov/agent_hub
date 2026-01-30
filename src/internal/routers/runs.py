from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories import get_run, list_iterations
from internal.dependencies import get_session
from internal.schemas.runs import (
    RunCreateRequest,
    RunLogEntry,
    RunLogsResponse,
    RunReportResponse,
    RunResponse,
    RunRetryRequest,
)
from services.runs_service import RunsService
from services.jobs import enqueue_run
from services.orchestrator import Orchestrator
from services.jobs import log_event

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
    logs = [
        RunLogEntry(
            message=log.message,
            kind=log.kind,
            payload=log.payload or {},
            created_at=log.created_at,
        )
        for log in run.logs
    ]
    return RunLogsResponse(run_id=run_id, logs=logs)


@router.get("/{run_id}/report", response_model=RunReportResponse)
async def get_run_report(
    run_id: str, session: AsyncSession = Depends(get_session)
) -> RunReportResponse:
    run = await get_run(session, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    iterations = await list_iterations(session, run_id)
    last = iterations[-1] if iterations else None
    return RunReportResponse(
        run_id=run.id,
        status=run.status,
        repo_url=run.repo_url,
        issue_number=run.issue_number or 0,
        model=run.model,
        max_iterations=run.max_iterations,
        iterations_count=len(iterations),
        last_iteration_index=last.index if last else None,
        last_ci_summary=last.ci_summary if last else None,
        last_reviewer_verdict=last.reviewer_verdict if last else None,
    )


@router.post("/issue/retry", response_model=RunResponse)
async def retry_issue(
    request: RunRetryRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
) -> RunResponse:
    service = RunsService()
    run = await service.get_latest_by_issue(session, request)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    iterations = await list_iterations(session, run.id)
    if len(iterations) >= run.max_iterations:
        raise HTTPException(status_code=400, detail="Max iterations reached")
    orchestrator = Orchestrator()
    if not orchestrator.can_transition(run.status, "NEEDS_FIX"):
        raise HTTPException(status_code=400, detail="Invalid state transition")
    run.status = orchestrator.advance(run.status, "NEEDS_FIX")
    await session.commit()
    await log_event(
        session,
        run.id,
        "Retry requested",
        "retry_requested",
        {"repo_url": run.repo_url, "issue_number": run.issue_number},
    )
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
