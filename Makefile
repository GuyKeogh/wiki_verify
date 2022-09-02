.PHONY: fmt
fmt:
	poetry run isort .
	poetry run black .

.PHONY: lint
lint:
	poetry run flake8 .

.PHONY: test
lint:
	poetry run pytest tests
	poetry run mypy .

.PHONY: check
check:
	make fmt lint test