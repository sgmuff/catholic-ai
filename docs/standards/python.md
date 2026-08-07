# Python standard

Most executable projects in this repository will be Python. This document is a layer on top of [`architecture.md`](architecture.md): it makes "test-first, standard command surface" concrete for that language instead of leaving each project to reinvent it. A project that copies [`docs/project-template/python-starter/`](../project-template/python-starter/) already satisfies everything below.

## Layout

Python projects use a `src/` layout, not a flat one — it forces tests to import the package the way an installed user would, rather than accidentally passing because they're sitting next to the source:

```
projects/<track>/<project-name>/
├── pyproject.toml
├── Makefile
├── src/
│   └── <package_name>/
│       └── __init__.py
└── tests/
    └── test_*.py
```

## Toolchain

One set of tools, used the same way in every project:

- **pytest** for tests. Test files are `test_*.py`, discovered under `tests/`.
- **ruff** for both linting and formatting — one tool instead of separately maintaining flake8/isort/black. Run as `ruff check` (lint) and `ruff format --check` (formatting).
- **mypy** for type checking, run in `make lint` rather than as a pre-commit hook — the mypy pre-commit mirror runs in an isolated environment that doesn't see a project's actual dependencies, which produces false-positive `import-untyped` errors often enough that it costs more trust than it's worth. Running it in CI, against the real installed environment, doesn't have that problem.
- **coverage.py** (via `pytest --cov`) to measure what the test suite actually exercises.

All four are declared as dependencies in `pyproject.toml`, not installed ad hoc, so `make setup` is what puts them on a contributor's machine.

## Coverage floor

CI fails a project's `test` target if coverage drops below **80%** of `src/`. That number is a floor, not a target — a project can and should set a higher bar for itself in its own `pyproject.toml` (`[tool.coverage.report] fail_under = ...`) if the work it does warrants it, but shouldn't go below 80 without a stated reason in its README.

## Standard `pyproject.toml` shape

```toml
[project]
name = "<project-name>"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-cov>=5", "ruff>=0.16", "mypy>=1.13"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.coverage.run]
source = ["src"]

[tool.coverage.report]
fail_under = 80

[tool.ruff]
line-length = 100

[tool.mypy]
python_version = "3.12"
strict = true

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

## Standard `Makefile` targets

```makefile
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
```

This is exactly what `.github/workflows/ci.yml`'s project-checks job runs (`make setup lint test`) for any project it finds — nothing project-specific needs to be added to CI for a Python project to be fully checked.

## Why not uv (yet)

`uv` is faster than `pip`/`venv`, but standardizing on it now would mean every contributor needs it installed before they can run `make setup`. `pip` and `venv` ship with Python itself, so they're the floor every project can rely on without an extra dependency. A project is free to use `uv` internally if it documents that requirement in its README's Stack section and its own `Makefile` reflects it — the standard here is the outer shape (`setup`/`lint`/`test` exist and work), not the tool underneath.
