from __future__ import annotations

from agents.base import AgentResult, BaseAgent


class TestAgent(BaseAgent):
    async def run(self, prompt: str) -> AgentResult:
        content = f"Tests for: {prompt}"
        return AgentResult(content=content, metadata={"agent": self.name})
