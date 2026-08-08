setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e ".[dev]"

lint:
	.venv/bin/ruff check .
	.venv/bin/ruff format --check .
	.venv/bin/mypy eval

test:
	.venv/bin/pytest --cov --cov-report=term-missing

sync-skill-bundle:
	.venv/bin/python -m eval.sync_skill_bundle
