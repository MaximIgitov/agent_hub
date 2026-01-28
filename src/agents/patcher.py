from __future__ import annotations

from agents.base import AgentResult, BaseAgent


class PatchAgent(BaseAgent):
    async def run(self, prompt: str) -> AgentResult:
        diff = f"diff --git a/file b/file\n--- a/file\n+++ b/file\n@@\n{prompt}"
        return AgentResult(content=diff, metadata={"agent": self.name})
