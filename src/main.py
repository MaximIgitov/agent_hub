from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from arq import create_pool
from arq.connections import RedisSettings

from config import settings
from db.base import create_engine, create_sessionmaker, init_models
from internal.routers.runs import router as runs_router
from internal.routers.settings import router as settings_router
from internal.routers.ui import router as ui_router
from internal.routers.webhooks import router as webhooks_router
from internal.routers.installations import router as installations_router
from llm.openrouter import default_client
from setup_logger import setup_logger
from services.jobs import run_issue_job

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_engine()
    sessionmaker = create_sessionmaker(engine)
    app.state.db_engine = engine
    app.state.db_sessionmaker = sessionmaker
    app.state.llm_client = default_client()
    try:
        app.state.redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    except Exception:
        app.state.redis = None
    await init_models(engine)
    logger.info("App started with model %s", settings.openrouter_model)
    yield
    if app.state.redis:
        await app.state.redis.close()
    await engine.dispose()


app = FastAPI(title="Agent Hub", lifespan=lifespan)
app.include_router(ui_router)
app.include_router(webhooks_router)
app.include_router(runs_router)
app.include_router(settings_router)
app.include_router(installations_router)


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    functions = [run_issue_job]

    async def startup(self, ctx) -> None:
        ctx["llm_client"] = default_client()
