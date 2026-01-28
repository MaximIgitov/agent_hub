from __future__ import annotations

from dataclasses import dataclass

import httpx

from github.permissions_policy import PermissionsPolicy, assert_can_push


@dataclass(slots=True)
class GitHubClient:
    token: str
    policy: PermissionsPolicy

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }

    async def create_comment(self, url: str, body: str) -> None:
        async with httpx.AsyncClient() as client:
            await client.post(url, headers=self._headers(), json={"body": body})

    async def create_review(self, url: str, body: str, event: str) -> None:
        async with httpx.AsyncClient() as client:
            await client.post(
                url,
                headers=self._headers(),
                json={"body": body, "event": event},
            )

    async def push_branch(self, url: str, payload: dict[str, str]) -> None:
        assert_can_push(self.policy)
        async with httpx.AsyncClient() as client:
            await client.post(url, headers=self._headers(), json=payload)

    async def set_status_label(self, url: str, label: str) -> None:
        async with httpx.AsyncClient() as client:
            await client.post(url, headers=self._headers(), json={"labels": [label]})
