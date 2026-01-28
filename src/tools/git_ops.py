from __future__ import annotations

import subprocess
from pathlib import Path


def run_git(repo_path: Path, args: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def init_repo(path: Path) -> None:
    run_git(path, ["init"])


def create_branch(repo_path: Path, name: str) -> None:
    run_git(repo_path, ["checkout", "-b", name])


def apply_diff(repo_path: Path, diff: str) -> bool:
    if not diff.strip():
        return False
    result = subprocess.run(
        ["git", "apply", "-"],
        input=diff.encode("utf-8"),
        cwd=str(repo_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode == 0


def commit_all(repo_path: Path, message: str) -> None:
    run_git(repo_path, ["add", "."])
    run_git(repo_path, ["commit", "-m", message])
