from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LLMResponse:
    content: str
    model: str


class LLMClient:
    async def complete(self, prompt: str) -> LLMResponse:
        raise NotImplementedError
