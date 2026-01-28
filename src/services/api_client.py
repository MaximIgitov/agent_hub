from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass(slots=True)
class AgentHubApiClient:
    base_url: str

    def create_run(self, payload: dict) -> dict:
        response = httpx.post(f"{self.base_url}/v1/runs/issue", json=payload, timeout=20)
        response.raise_for_status()
        return response.json()

    def list_runs(self) -> list[dict]:
        response = httpx.get(f"{self.base_url}/v1/runs", timeout=20)
        response.raise_for_status()
        return response.json()
