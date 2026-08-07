# Python project starter

Copy this whole directory to `<project-name>/` at the repository root, then:

1. Rename `src/example_package/` to your project's actual package name (use underscores; match it to `[project].name` in `pyproject.toml`, written with hyphens per convention).
2. Update `pyproject.toml`'s `name` field to match.
3. Replace `src/example_package/core.py` and `tests/test_core.py` with your actual code and tests — but keep the pattern: a test exists for every piece of behavior before (or alongside) the code that implements it.
4. Delete this README and fill in `<project-name>/README.md` from [`docs/project-template/README.template.md`](../README.template.md) instead.
5. Run `make setup lint test` and confirm it passes clean before committing.

This skeleton already satisfies [`docs/standards/python.md`](../../standards/python.md) as written — `src/` layout, pytest, ruff, mypy, an 80% coverage floor, and a `Makefile` with `setup`/`lint`/`test` that `.github/workflows/ci.yml` picks up automatically. You shouldn't need to touch the tooling configuration, only the code.
