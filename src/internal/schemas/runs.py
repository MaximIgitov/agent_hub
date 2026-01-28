from __future__ import annotations

from pydantic import BaseModel


class RunCreateRequest(BaseModel):
    repo_url: str
    issue_number: int
    model: str
    max_iters: int = 5


class RunResponse(BaseModel):
    run_id: str
    status: str
    repo_url: str
    issue_number: int
    model: str
    max_iterations: int


class RunLogsResponse(BaseModel):
    run_id: str
    logs: list[str]
