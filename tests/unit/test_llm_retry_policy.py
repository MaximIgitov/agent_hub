import json

import httpx
import pytest

from llm.openrouter import OpenRouterClient


@pytest.mark.asyncio
async def test_llm_retries_on_429() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] < 3:
            return httpx.Response(429, json={"error": "rate limit"})
        payload = {"choices": [{"message": {"content": "ok"}}]}
        return httpx.Response(200, content=json.dumps(payload))

    transport = httpx.MockTransport(handler)
    client = OpenRouterClient(api_key="x", model="y", transport=transport)
    response = await client.complete("hello")
    assert response.content == "ok"
    assert calls["count"] == 3
