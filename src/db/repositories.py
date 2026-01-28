from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import EventLog, Iteration, Run


async def create_run(session: AsyncSession, run: Run) -> Run:
    session.add(run)
    await session.commit()
    await session.refresh(run)
    return run


async def get_run(session: AsyncSession, run_id: str) -> Optional[Run]:
    result = await session.execute(select(Run).where(Run.id == run_id))
    return result.scalar_one_or_none()


async def list_runs(session: AsyncSession) -> list[Run]:
    result = await session.execute(select(Run).order_by(Run.created_at.desc()))
    return list(result.scalars().all())


async def add_log(session: AsyncSession, log: EventLog) -> EventLog:
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


async def add_iteration(session: AsyncSession, iteration: Iteration) -> Iteration:
    session.add(iteration)
    await session.commit()
    await session.refresh(iteration)
    return iteration


async def list_iterations(session: AsyncSession, run_id: str) -> list[Iteration]:
    result = await session.execute(
        select(Iteration).where(Iteration.run_id == run_id).order_by(Iteration.index)
    )
    return list(result.scalars().all())
