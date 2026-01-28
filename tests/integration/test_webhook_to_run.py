import httpx

from config import settings
from main import app


def test_webhook_accepts_event(tmp_path) -> None:
    settings.database_url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    settings.github_webhook_secret = ""
    transport = httpx.ASGITransport(app=app, lifespan="on")
    with httpx.Client(transport=transport, base_url="http://test") as client:
        response = client.post("/v1/webhooks/github", content=b"{}")
    assert response.status_code == 200
