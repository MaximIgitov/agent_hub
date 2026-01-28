from __future__ import annotations

from dataclasses import dataclass

from github.client import GitHubClient
from github.permissions_policy import CODE_POLICY


@dataclass(slots=True)
class CodeAgentService:
    token: str

    def client(self) -> GitHubClient:
        return GitHubClient(token=self.token, policy=CODE_POLICY)
