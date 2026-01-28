from pathlib import Path

from tools.git_ops import apply_diff, commit_all, create_branch, init_repo, run_git


def test_git_ops_fake_repo(tmp_path: Path) -> None:
    init_repo(tmp_path)
    run_git(tmp_path, ["config", "user.email", "bot@example.com"])
    run_git(tmp_path, ["config", "user.name", "bot"])
    create_branch(tmp_path, "agent/test")
    diff = "diff --git a/a b/a\nnew file mode 100644\n--- /dev/null\n+++ b/a\n@@\n+hi\n"
    assert apply_diff(tmp_path, diff) is True
    commit_all(tmp_path, "add file a")
    log = run_git(tmp_path, ["log", "--oneline"]).stdout.decode("utf-8")
    assert "add file a" in log
