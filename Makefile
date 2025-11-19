.PHONY: install lint format typecheck test ci

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

lint:
	ruff check .

format:
	black .
	ruff check --fix .

typecheck:
	mypy .

# Run fast feedback: lint + type-check + tests
ci: lint typecheck test

# Run pytest with defaults
test:
	pytest
