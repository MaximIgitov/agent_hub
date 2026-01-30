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
    await log_event(
        session,
        run.id,
        "Planned",
        "state_transition",
        {"state": run.status},
    )

    run.status = orchestrator.advance(run.status, "CODING")
    await log_event(
        session,
        run.id,
        "Coding",
        "state_transition",
        {"state": run.status},
    )

    planner_prompt = {
        "repo_url": run.repo_url,
        "issue_number": run.issue_number,
        "model": run.model,
    }
    await log_event(
        session,
        run.id,
        "Planner prompt built",
        "planner_prompt",
        planner_prompt,
    )
    plan = "Initial plan"
    await log_event(
        session,
        run.id,
        "Planner output",
        "planner_output",
        {"plan": plan},
    )
    diff = "diff --git a/file b/file\n--- a/file\n+++ b/file\n@@\n+placeholder\n"
    patch_hash = hash_diff(diff)
    await log_event(
        session,
        run.id,
        "Patch generated",
        "patch_generated",
        {"diff": diff, "patch_hash": patch_hash},
    )
    previous_hash = iterations[-1].patch_hash if iterations else None
    noop_result = check_noop(diff, previous_hash)
    scope_result = check_scope(diff)
    if not noop_result.ok or not scope_result.ok or is_noop(diff):
        run.status = orchestrator.advance(run.status, "FAILED")
        await log_event(
            session,
            run.id,
            f"Guardrail stop: {noop_result.reason}, {scope_result.reason}",
            "guardrail_stop",
            {
                "noop": noop_result.reason,
                "scope": scope_result.reason,
            },
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
    await log_event(
        session,
        run.id,
        "PR opened",
        "state_transition",
        {"state": run.status},
    )
    run.status = orchestrator.advance(run.status, "CI_RUNNING")
    await log_event(
        session,
        run.id,
        "CI running",
        "state_transition",
        {"state": run.status},
    )
    await log_event(
        session,
        run.id,
        "CI summary",
        "ci_summary",
        {"summary": "pending"},
    )
    run.status = orchestrator.advance(run.status, "REVIEWING")
    await log_event(
        session,
        run.id,
        "Reviewing",
        "state_transition",
        {"state": run.status},
    )
    await log_event(
        session,
        run.id,
        "Reviewer verdict",
        "review_verdict",
        {"verdict": "pending"},
    )
    run.status = orchestrator.advance(run.status, "DONE")
    await log_event(
        session,
        run.id,
        "Done",
        "state_transition",
        {"state": run.status},
    )


async def enqueue_run(redis: ArqRedis, run_id: str) -> None:
    await redis.enqueue_job("run_issue_job", run_id)


async def log_event(
    session: AsyncSession, run_id: str, message: str, kind: str, payload: dict
) -> None:
    await add_log(
        session,
        EventLog(
            id=str(uuid4()),
            run_id=run_id,
            message=message,
            kind=kind,
            payload=payload,
        ),
    )
