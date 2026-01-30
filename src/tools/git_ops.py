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


def clone_repo(repo_url: str, dest: Path) -> None:
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(dest)],
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
        ["git", "apply", "--3way", "--whitespace=fix", "-"],
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


def list_files(repo_path: Path) -> list[str]:
    result = run_git(repo_path, ["ls-files"])
    if result.returncode != 0:
        return []
    return result.stdout.decode("utf-8").splitlines()


def push_branch(repo_path: Path, branch: str, remote: str = "origin") -> None:
    run_git(repo_path, ["push", remote, branch])
