from __future__ import annotations

from uuid import uuid4

from arq import ArqRedis
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import create_engine, create_sessionmaker
from db.models import EventLog, Iteration, Run
from db.repositories import add_iteration, add_log, get_run, list_iterations
from services.orchestrator import Orchestrator
from tools.guardrails import check_noop, check_scope
from tools.diff_ops import hash_diff, is_noop


async def run_issue_job(ctx: dict, run_id: str) -> None:
    engine = create_engine()
    sessionmaker = create_sessionmaker(engine)
    async with sessionmaker() as session:
        await _run_issue(session, run_id)
    await engine.dispose()


async def _run_issue(session: AsyncSession, run_id: str) -> None:
    run = await get_run(session, run_id)
    if not run:
        return
    iterations = await list_iterations(session, run.id)
    if len(iterations) >= run.max_iterations:
        return
    orchestrator = Orchestrator()
    run.status = orchestrator.advance(run.status, "PLANNED")
    await add_log(session, EventLog(id=str(uuid4()), run_id=run.id, message="Planned"))

    run.status = orchestrator.advance(run.status, "CODING")
    await add_log(session, EventLog(id=str(uuid4()), run_id=run.id, message="Coding"))

    plan = "Initial plan"
    diff = "diff --git a/file b/file\n--- a/file\n+++ b/file\n@@\n+placeholder\n"
    patch_hash = hash_diff(diff)
    previous_hash = iterations[-1].patch_hash if iterations else None
    noop_result = check_noop(diff, previous_hash)
    scope_result = check_scope(diff)
    if not noop_result.ok or not scope_result.ok or is_noop(diff):
        run.status = orchestrator.advance(run.status, "FAILED")
        await add_log(
            session,
            EventLog(
                id=str(uuid4()),
                run_id=run.id,
                message=f"Guardrail stop: {noop_result.reason}, {scope_result.reason}",
            ),
        )
        return
    iteration = Iteration(
        id=str(uuid4()),
        run_id=run.id,
        index=len(iterations) + 1,
        plan=plan,
        patch_hash=patch_hash,
        ci_summary="pending",
        reviewer_verdict="pending",
    )
    await add_iteration(session, iteration)
    run.status = orchestrator.advance(run.status, "PR_OPENED")
    await add_log(session, EventLog(id=str(uuid4()), run_id=run.id, message="PR opened"))
    run.status = orchestrator.advance(run.status, "CI_RUNNING")
    await add_log(session, EventLog(id=str(uuid4()), run_id=run.id, message="CI running"))
    run.status = orchestrator.advance(run.status, "REVIEWING")
    await add_log(session, EventLog(id=str(uuid4()), run_id=run.id, message="Reviewing"))
    run.status = orchestrator.advance(run.status, "DONE")
    await add_log(session, EventLog(id=str(uuid4()), run_id=run.id, message="Done"))


async def enqueue_run(redis: ArqRedis, run_id: str) -> None:
    await redis.enqueue_job("run_issue_job", run_id)
