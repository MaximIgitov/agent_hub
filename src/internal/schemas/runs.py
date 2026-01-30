from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class RunCreateRequest(BaseModel):
    repo_url: str
    issue_number: int
    model: str
    max_iters: int = 5


class RunRetryRequest(BaseModel):
    repo_url: str
    issue_number: int


class RunResponse(BaseModel):
    run_id: str
    status: str
    repo_url: str
    issue_number: int
    model: str
    max_iterations: int


class RunLogsResponse(BaseModel):
    run_id: str

    logs: list["RunLogEntry"]


class RunLogEntry(BaseModel):
    message: str
    kind: str
    payload: dict
    created_at: datetime


class RunReportResponse(BaseModel):
    run_id: str
    status: str
    repo_url: str
    issue_number: int
    model: str
    max_iterations: int
    iterations_count: int
    last_iteration_index: int | None
    last_ci_summary: str | None
    last_reviewer_verdict: str | None
