import httpx
import pytest

from config import settings
from db.base import create_engine, create_sessionmaker, init_models
from main import app


@pytest.mark.asyncio
async def test_webhook_accepts_event(tmp_path) -> None:
    settings.database_url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    settings.github_webhook_secret = ""
    engine = create_engine()
    sessionmaker = create_sessionmaker(engine)
    app.state.db_engine = engine
    app.state.db_sessionmaker = sessionmaker
    app.state.redis = None
    await init_models(engine)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/v1/webhooks/github", content=b"{}")
    await engine.dispose()
    assert response.status_code == 200
