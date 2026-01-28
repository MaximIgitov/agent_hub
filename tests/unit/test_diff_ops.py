from pathlib import Path

from tools.diff_ops import apply_check, hash_diff, is_noop, is_same_hash
from tools.git_ops import init_repo


def test_hash_and_noop() -> None:
    diff = "diff --git a/a b/a\n--- a/a\n+++ b/a\n@@\n+hi\n"
    assert not is_noop(diff)
    assert is_noop("   \n")
    assert is_same_hash(hash_diff(diff), hash_diff(diff))


def test_apply_check(tmp_path: Path) -> None:
    init_repo(tmp_path)
    diff = "diff --git a/a b/a\nnew file mode 100644\n--- /dev/null\n+++ b/a\n@@\n+hi\n"
    assert apply_check(tmp_path, diff) is True
