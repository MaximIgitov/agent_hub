lint:
	ruff check .
	black --check .
	mypy src

test:
	pytest
