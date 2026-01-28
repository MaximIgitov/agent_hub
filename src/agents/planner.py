from __future__ import annotations

from agents.base import AgentResult, BaseAgent


class PlannerAgent(BaseAgent):
    async def run(self, prompt: str) -> AgentResult:
        plan = f"Plan: {prompt}"
        return AgentResult(content=plan, metadata={"agent": self.name})
