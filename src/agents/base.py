from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AgentResult:
    content: str
    metadata: dict[str, str]


@dataclass(slots=True)
class BaseAgent:
    name: str

    async def run(self, prompt: str) -> AgentResult:
        return AgentResult(content=prompt, metadata={"agent": self.name})
