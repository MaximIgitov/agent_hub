from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/v1/installations", tags=["installations"])


@router.post("/{installation_id}/repos/{owner}/{repo}/connect")
async def connect_repo(installation_id: int, owner: str, repo: str) -> dict[str, str]:
    return {
        "installation_id": str(installation_id),
        "repo": f"{owner}/{repo}",
        "status": "connected",
    }
