from __future__ import annotations

from dataclasses import dataclass

from config import settings
from tools.diff_ops import diff_stats, hash_diff, is_noop, is_same_hash


@dataclass(slots=True)
class GuardrailResult:
    ok: bool
    reason: str


def check_noop(diff: str, previous_hash: str | None) -> GuardrailResult:
    if is_noop(diff):
        return GuardrailResult(False, "diff is empty")
    current_hash = hash_diff(diff)
    if previous_hash and is_same_hash(previous_hash, current_hash):
        return GuardrailResult(False, "diff hash is identical")
    return GuardrailResult(True, "ok")


def check_scope(diff: str) -> GuardrailResult:
    files, lines = diff_stats(diff)
    if files > settings.max_patch_files:
        return GuardrailResult(False, "too many files touched")
    if lines > settings.max_patch_lines:
        return GuardrailResult(False, "too many lines touched")
    return GuardrailResult(True, "ok")


def check_positive_progress(previous_errors: int, current_errors: int) -> GuardrailResult:
    if current_errors < previous_errors:
        return GuardrailResult(True, "ci errors reduced")
    if current_errors == 0:
        return GuardrailResult(True, "ci green")
    return GuardrailResult(False, "no positive progress")
