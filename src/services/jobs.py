from __future__ import annotations

from uuid import uuid4
from pathlib import Path
import tempfile
from urllib.parse import urlparse

from arq import ArqRedis
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.base import create_engine, create_sessionmaker
from db.models import EventLog, Iteration, Run
from db.repositories import add_iteration, add_log, get_run, list_iterations
from github.client import GitHubClient
from github.permissions_policy import CODE_POLICY
from llm.openrouter import OpenRouterClient
from services.orchestrator import Orchestrator
from tools.guardrails import check_noop, check_scope
from tools.diff_ops import hash_diff, is_noop
from tools.git_ops import apply_diff, clone_repo, commit_all, create_branch, list_files, push_branch


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
    if run.status == "NEEDS_FIX":
        await advance_state(session, run, orchestrator, "CODING")
    else:
        await advance_state(session, run, orchestrator, "PLANNED")
        await advance_state(session, run, orchestrator, "CODING")

    if not settings.github_token:
        await fail_run(session, run, orchestrator, "Missing AGENT_HUB_GITHUB_TOKEN")
        return
    if not settings.openrouter_api_key:
        await fail_run(session, run, orchestrator, "Missing AGENT_HUB_OPENROUTER_API_KEY")
        return

    if not run.issue_number or run.issue_number <= 0:
        await fail_run(session, run, orchestrator, "Missing issue_number")
        return

    owner, repo = parse_repo(run.repo_url)
    if not owner or not repo:
        await fail_run(session, run, orchestrator, "Invalid repo_url")
        return

    github = GitHubClient(token=settings.github_token, policy=CODE_POLICY)
    issue = await github.get_issue(owner, repo, run.issue_number or 0)
    repo_info = await github.get_repo(owner, repo)
    default_branch = repo_info.get("default_branch", "main")

    planner_prompt = build_planner_prompt(issue)
    await log_event(
        session,
        run.id,
        "Planner prompt built",
        "planner_prompt",
        {"prompt": planner_prompt},
    )
    llm = OpenRouterClient(
        api_key=settings.openrouter_api_key,
        model=run.model or settings.openrouter_model,
    )
    plan_response = await llm.complete(planner_prompt, correlation_id=run.id)
    plan = plan_response.content.strip()
    await log_event(
        session,
        run.id,
        "Planner output",
        "planner_output",
        {"plan": plan},
    )

    workspace = Path(tempfile.mkdtemp(prefix=f"agent_hub_{run.id}_"))
    repo_path = workspace / "repo"
    clone_repo(auth_repo_url(run.repo_url), repo_path)
    if not (repo_path / ".git").exists():
        await fail_run(session, run, orchestrator, "Failed to clone repo")
        return

    branch = f"agent/run-{run.id[:8]}-it{len(iterations) + 1}"
    create_branch(repo_path, branch)

    files = list_files(repo_path)
    patch_prompt = build_patch_prompt(issue, plan, files)
    await log_event(
        session,
        run.id,
        "Patch prompt built",
        "patch_prompt",
        {"prompt": patch_prompt},
    )
    patch_response = await llm.complete(patch_prompt, correlation_id=run.id)
    diff = extract_diff(patch_response.content)
    if not diff.strip():
        await fail_run(session, run, orchestrator, "Empty diff from model")
        return

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
        await fail_run(
            session,
            run,
            orchestrator,
            f"Guardrail stop: {noop_result.reason}, {scope_result.reason}",
            payload={"noop": noop_result.reason, "scope": scope_result.reason},
        )
        return

    if not apply_diff(repo_path, diff):
        await fail_run(session, run, orchestrator, "Failed to apply diff")
        return

    commit_all(repo_path, f"Agent: issue #{run.issue_number}")
    push_branch(repo_path, branch)

    pr_title = f"Agent: {issue.get('title', 'Issue')} (#{run.issue_number})"
    pr_body = f"Automated changes for issue #{run.issue_number}.\n\nPlan:\n{plan}"
    pr = await github.create_pull_request(
        owner, repo, pr_title, branch, default_branch, pr_body
    )
    await log_event(
        session,
        run.id,
        "PR opened",
        "pr_opened",
        {"url": pr.get("html_url", ""), "branch": branch},
    )

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

    await advance_state(session, run, orchestrator, "PR_OPENED")
    await advance_state(session, run, orchestrator, "CI_RUNNING")
    await log_event(session, run.id, "CI summary", "ci_summary", {"summary": "pending"})
    await advance_state(session, run, orchestrator, "REVIEWING")


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


def parse_repo(repo_url: str) -> tuple[str, str]:
    if repo_url.startswith("git@github.com:"):
        owner_repo = repo_url.split(":", 1)[1].replace(".git", "")
        parts = owner_repo.split("/")
        if len(parts) == 2:
            return parts[0], parts[1]
        return "", ""
    parsed = urlparse(repo_url)
    path = parsed.path.strip("/").replace(".git", "")
    parts = path.split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return "", ""


def auth_repo_url(repo_url: str) -> str:
    if not settings.github_token:
        return repo_url
    if repo_url.startswith("git@github.com:"):
        owner_repo = repo_url.split(":", 1)[1].replace(".git", "")
        return f"https://x-access-token:{settings.github_token}@github.com/{owner_repo}.git"
    parsed = urlparse(repo_url)
    if parsed.scheme in {"http", "https"} and parsed.netloc == "github.com":
        return (
            f"https://x-access-token:{settings.github_token}@github.com"
            f"{parsed.path}"
        )
    return repo_url


def build_planner_prompt(issue: dict) -> str:
    title = issue.get("title", "")
    body = issue.get("body", "")
    return (
        "You are a software engineer planning changes for a GitHub issue.\n"
        "Provide a concise, actionable plan in bullet points.\n\n"
        f"Issue title: {title}\n"
        f"Issue body:\n{body}\n"
    )


def build_patch_prompt(issue: dict, plan: str, files: list[str]) -> str:
    title = issue.get("title", "")
    body = issue.get("body", "")
    files_block = "\n".join(files[:200])
    return (
        "You are a code agent. Generate a unified git diff that solves the issue.\n"
        "Output ONLY the diff. Do not include explanations or code fences.\n"
        "Make sure paths match repository files. Keep changes minimal.\n\n"
        f"Issue title: {title}\n"
        f"Issue body:\n{body}\n\n"
        f"Plan:\n{plan}\n\n"
        f"Repository files (top 200):\n{files_block}\n"
    )


def extract_diff(text: str) -> str:
    lines = text.strip().splitlines()
    if not lines:
        return ""
    if lines[0].startswith("```"):
        lines = lines[1:]
        if lines and lines[0].strip().lower() == "diff":
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
    return "\n".join(lines).strip()


async def advance_state(
    session: AsyncSession, run: Run, orchestrator: Orchestrator, next_state: str
) -> None:
    run.status = orchestrator.advance(run.status, next_state)
    await session.commit()
    await log_event(
        session,
        run.id,
        f"State -> {run.status}",
        "state_transition",
        {"state": run.status},
    )


async def fail_run(
    session: AsyncSession,
    run: Run,
    orchestrator: Orchestrator,
    reason: str,
    payload: dict | None = None,
) -> None:
    run.status = orchestrator.advance(run.status, "FAILED")
    await session.commit()
    await log_event(
        session,
        run.id,
        f"Failed: {reason}",
        "failed",
        payload or {"reason": reason},
    )
