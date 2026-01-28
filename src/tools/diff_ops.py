from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


def hash_diff(diff: str) -> str:
    return hashlib.sha256(diff.encode("utf-8")).hexdigest()


def is_noop(diff: str) -> bool:
    return not diff.strip()


def is_same_hash(current_hash: str, previous_hash: str) -> bool:
    return current_hash == previous_hash


def apply_check(repo_path: Path, diff: str) -> bool:
    if is_noop(diff):
        return False
    result = subprocess.run(
        ["git", "apply", "--check", "-"],
        input=diff.encode("utf-8"),
        cwd=str(repo_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode == 0


def apply_check_3way(repo_path: Path, diff: str) -> bool:
    if is_noop(diff):
        return False
    result = subprocess.run(
        ["git", "apply", "--3way", "--check", "-"],
        input=diff.encode("utf-8"),
        cwd=str(repo_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode == 0


def diff_stats(diff: str) -> tuple[int, int]:
    files = 0
    lines = 0
    for line in diff.splitlines():
        if line.startswith("diff --git"):
            files += 1
        if line.startswith("+") and not line.startswith("+++"):
            lines += 1
        if line.startswith("-") and not line.startswith("---"):
            lines += 1
    return files, lines
