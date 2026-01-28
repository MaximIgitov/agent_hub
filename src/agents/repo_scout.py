from __future__ import annotations

from agents.base import AgentResult, BaseAgent


class RepoScoutAgent(BaseAgent):
    async def run(self, prompt: str) -> AgentResult:
        summary = f"Repo scout found targets for: {prompt}"
        return AgentResult(content=summary, metadata={"agent": self.name})
