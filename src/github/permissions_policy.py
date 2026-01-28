from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PermissionsPolicy:
    allow_push: bool
    allow_review: bool
    allow_comment: bool


CODE_POLICY = PermissionsPolicy(allow_push=True, allow_review=True, allow_comment=True)
REVIEW_POLICY = PermissionsPolicy(allow_push=False, allow_review=True, allow_comment=True)


def assert_can_push(policy: PermissionsPolicy) -> None:
    if not policy.allow_push:
        raise PermissionError("Policy forbids pushing code")
