from __future__ import annotations

import re


def parse_ruff(log: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    pattern = re.compile(r"^(?P<file>[^:]+):(?P<line>\d+):(?P<col>\d+): (?P<code>\w+) (?P<msg>.+)$")
    for line in log.splitlines():
        match = pattern.match(line.strip())
        if match:
            findings.append(match.groupdict())
    return findings


def parse_mypy(log: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    pattern = re.compile(r"^(?P<file>[^:]+):(?P<line>\d+): (?P<severity>error|note): (?P<msg>.+)$")
    for line in log.splitlines():
        match = pattern.match(line.strip())
        if match:
            findings.append(match.groupdict())
    return findings


def parse_pytest(log: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    pattern = re.compile(r"^FAILED (?P<test>[^ ]+) - (?P<msg>.+)$")
    for line in log.splitlines():
        match = pattern.match(line.strip())
        if match:
            findings.append(match.groupdict())
    return findings


def parse_build(log: str) -> dict[str, str]:
    for line in log.splitlines():
        if "ERROR" in line or "Error" in line:
            return {"first_failure": line.strip()}
    return {"first_failure": ""}
