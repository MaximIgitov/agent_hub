from tools.ci_parser import parse_build, parse_mypy, parse_pytest, parse_ruff


def test_parse_ruff() -> None:
    log = "src/app.py:10:4: F401 unused import\n"
    result = parse_ruff(log)
    assert result[0]["code"] == "F401"


def test_parse_mypy() -> None:
    log = "src/app.py:3: error: Incompatible types\n"
    result = parse_mypy(log)
    assert result[0]["severity"] == "error"


def test_parse_pytest() -> None:
    log = "FAILED tests/test_app.py::test_health - AssertionError: boom\n"
    result = parse_pytest(log)
    assert result[0]["test"] == "tests/test_app.py::test_health"


def test_parse_build() -> None:
    log = "Step 1\nError: build failed\n"
    result = parse_build(log)
    assert "build failed" in result["first_failure"]
