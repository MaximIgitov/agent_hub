from __future__ import annotations

from agents.base import AgentResult, BaseAgent


class CIHealerAgent(BaseAgent):
    async def run(self, prompt: str) -> AgentResult:
        content = f"Fix suggestion for CI: {prompt}"
        return AgentResult(content=content, metadata={"agent": self.name})
