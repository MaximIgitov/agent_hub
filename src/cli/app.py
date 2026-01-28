from __future__ import annotations

import typer

from config import settings
from services.api_client import AgentHubApiClient

app = typer.Typer(help="Agent Hub CLI")
issue_app = typer.Typer(help="Issue workflow")
pr_app = typer.Typer(help="PR workflow")
local_app = typer.Typer(help="Local workflow")


@issue_app.command("run")
def issue_run(
    repo: str,
    issue: int,
    model: str,
    max_iters: int = 5,
    api_url: str = settings.app_base_url,
) -> None:
    client = AgentHubApiClient(base_url=api_url)
    payload = {
        "repo_url": repo,
        "issue_number": issue,
        "model": model,
        "max_iters": max_iters,
    }
    run = client.create_run(payload)
    typer.echo(f"Run created: {run.get('run_id')}")


@pr_app.command("fix")
def pr_fix(repo: str, pr: int) -> None:
    typer.echo(f"PR fix queued for {repo}#{pr}")


@local_app.command("run")
def local_run(path: str, issue_text: str) -> None:
    typer.echo(f"Local run on {path} with issue: {issue_text}")


app.add_typer(issue_app, name="issue")
app.add_typer(pr_app, name="pr")
app.add_typer(local_app, name="local")
