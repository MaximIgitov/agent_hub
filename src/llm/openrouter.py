from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass

import httpx

from config import settings
from llm.base import LLMClient, LLMResponse


@dataclass(slots=True)
class OpenRouterClient(LLMClient):
    api_key: str
    model: str
    transport: httpx.AsyncBaseTransport | None = None

    async def complete(self, prompt: str, correlation_id: str | None = None) -> LLMResponse:
        retries = 3
        backoff = 0.5
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if correlation_id:
            headers["X-Request-Id"] = correlation_id
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=20, transport=self.transport) as client:
                    response = await client.post(url, json=payload, headers=headers)
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise httpx.HTTPError("retryable")
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return LLMResponse(content=content, model=self.model)
            except Exception:
                if attempt == retries - 1:
                    raise
                jitter = random.random() * 0.2
                await asyncio.sleep(backoff + jitter)
                backoff *= 2


def default_client() -> OpenRouterClient:
    return OpenRouterClient(
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_model,
    )
