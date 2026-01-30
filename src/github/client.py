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

    async def get_repo(self, owner: str, repo: str) -> dict:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers())
            response.raise_for_status()
            return response.json()

    async def get_issue(self, owner: str, repo: str, number: int) -> dict:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers())
            response.raise_for_status()
            return response.json()

    async def create_pull_request(
        self, owner: str, repo: str, title: str, head: str, base: str, body: str
    ) -> dict:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        payload = {"title": title, "head": head, "base": base, "body": body}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()
            return response.json()

    async def get_pull_request(self, owner: str, repo: str, number: int) -> dict:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers())
            response.raise_for_status()
            return response.json()

    async def list_pull_files(self, owner: str, repo: str, number: int) -> list[dict]:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}/files"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers(), params={"per_page": 100})
            response.raise_for_status()
            return response.json()

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
