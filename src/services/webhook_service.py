from __future__ import annotations

import hmac
import hashlib
import json

from config import settings
from setup_logger import setup_logger

logger = setup_logger(__name__)


class WebhookService:
    def verify_signature(self, payload: bytes, signature: str | None) -> bool:
        if not settings.github_webhook_secret:
            return True
        if not signature:
            return False
        digest = hmac.new(
            settings.github_webhook_secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
        expected = f"sha256={digest}"
        return hmac.compare_digest(expected, signature)

    async def handle_event(self, event: str, payload: bytes) -> None:
        data = json.loads(payload.decode("utf-8") or "{}")
        action = data.get("action", "")
        logger.info("Received event %s:%s (%d bytes)", event, action, len(payload))
        if event in {"issues", "issue_comment", "pull_request", "pull_request_review", "workflow_run", "check_suite"}:
            logger.info("Handling webhook event %s:%s", event, action)
