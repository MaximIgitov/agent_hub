from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    repo_url: Mapped[str] = mapped_column(String(512))
    issue_number: Mapped[Optional[int]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="NEW")
    model: Mapped[str] = mapped_column(String(128))
    max_iterations: Mapped[int] = mapped_column(default=5)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    iterations: Mapped[List["Iteration"]] = relationship(
        back_populates="run", lazy="selectin"
    )
    logs: Mapped[List["EventLog"]] = relationship(back_populates="run", lazy="selectin")


class Iteration(Base):
    __tablename__ = "iterations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"))
    index: Mapped[int] = mapped_column()
    plan: Mapped[str] = mapped_column(Text)
    patch_hash: Mapped[str] = mapped_column(String(64))
    ci_summary: Mapped[str] = mapped_column(Text)
    reviewer_verdict: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    run: Mapped["Run"] = relationship(back_populates="iterations", lazy="selectin")


class EventLog(Base):
    __tablename__ = "event_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"))
    message: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(64), default="event")
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    run: Mapped["Run"] = relationship(back_populates="logs", lazy="selectin")
