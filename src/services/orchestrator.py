from __future__ import annotations

from dataclasses import dataclass


STATES = {
    "NEW",
    "PLANNED",
    "CODING",
    "PR_OPENED",
    "CI_RUNNING",
    "REVIEWING",
    "NEEDS_FIX",
    "DONE",
    "FAILED",
}

TRANSITIONS = {
    "NEW": {"PLANNED"},
    "PLANNED": {"CODING"},
    "CODING": {"PR_OPENED", "FAILED"},
    "PR_OPENED": {"CI_RUNNING", "FAILED"},
    "CI_RUNNING": {"REVIEWING", "NEEDS_FIX", "FAILED"},
    "REVIEWING": {"DONE", "NEEDS_FIX", "FAILED"},
    "NEEDS_FIX": {"CODING", "FAILED"},
    "DONE": set(),
    "FAILED": set(),
}


@dataclass(slots=True)
class Orchestrator:
    def can_transition(self, current: str, target: str) -> bool:
        if current not in STATES or target not in STATES:
            return False
        return target in TRANSITIONS[current]

    def advance(self, current: str, target: str) -> str:
        if not self.can_transition(current, target):
            raise ValueError(f"Invalid transition {current} -> {target}")
        return target
