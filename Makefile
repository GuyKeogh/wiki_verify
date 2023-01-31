.PHONY: fmt
fmt:
	poetry run isort .
	poetry run black .

.PHONY: lint
lint:
	poetry run flake8 .
	poetry run mypy . --ignore-missing-imports

.PHONY: test
test:
	PYTHONPATH=. poetry run pytest tests

.PHONY: check
check:
	make fmt lint test
