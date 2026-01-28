import pytest

from services.orchestrator import Orchestrator


def test_state_transitions() -> None:
    orch = Orchestrator()
    assert orch.advance("NEW", "PLANNED") == "PLANNED"
    assert orch.advance("PLANNED", "CODING") == "CODING"


def test_invalid_transition() -> None:
    orch = Orchestrator()
    with pytest.raises(ValueError):
        orch.advance("NEW", "DONE")
