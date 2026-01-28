from __future__ import annotations

import json

from agents.base import AgentResult, BaseAgent


class ReviewerAgent(BaseAgent):
    async def run(self, prompt: str) -> AgentResult:
        verdict = {"verdict": "comment", "reason": "needs more evidence"}
        content = (
            f"Review summary for: {prompt}\n"
            f"Inline notes: none\n"
            f"{json.dumps(verdict)}"
        )
        return AgentResult(content=content, metadata={"agent": self.name})
