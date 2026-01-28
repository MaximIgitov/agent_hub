from __future__ import annotations

from dataclasses import dataclass

from github.client import GitHubClient
from github.permissions_policy import REVIEW_POLICY


@dataclass(slots=True)
class ReviewerService:
    token: str

    def client(self) -> GitHubClient:
        return GitHubClient(token=self.token, policy=REVIEW_POLICY)
