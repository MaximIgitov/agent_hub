from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class IssueEvent:
    action: str
    issue_number: int
    repo_full_name: str


@dataclass(slots=True)
class PullRequestEvent:
    action: str
    pr_number: int
    repo_full_name: str
