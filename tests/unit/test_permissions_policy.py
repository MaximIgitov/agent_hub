import pytest

from github.permissions_policy import REVIEW_POLICY, assert_can_push


def test_reviewer_cannot_push() -> None:
    with pytest.raises(PermissionError):
        assert_can_push(REVIEW_POLICY)
