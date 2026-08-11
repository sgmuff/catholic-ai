.PHONY: setup lint test sync-skill-bundle check-framework-freshness

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e ".[dev]"

lint:
	.venv/bin/ruff check .
	.venv/bin/ruff format --check .
	.venv/bin/mypy src

test:
	.venv/bin/pytest --cov --cov-report=term-missing

sync-skill-bundle:
	.venv/bin/python eval/sync_skill_bundle.py

check-framework-freshness:
	.venv/bin/python eval/check_framework_freshness.py
