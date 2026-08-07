# Architecture standards

This repository holds independent projects rather than one application, so it does not mandate a single language or framework. What it mandates is that every project is legible in the same way — that a contributor who has never seen a given project can find its tests, run them, and trust the result.

## Test-driven development

Every project with executable logic is built test-first: the test that describes the desired behavior is written before, or alongside, the code that satisfies it. A project does not merge with a red test suite, and a bug fix is not considered complete until a test exists that would have caught it.

This applies to scripts bundled with a Skill as much as to a standalone application. A script that fills out a risk-assessment template or parses a policy document is still logic, and still earns a test.

Projects that are not code — a policy template, a written framework, a set of talking points — don't have a test suite to write. They have a review checklist instead, covering accuracy of citation, internal consistency, and fitness for the audience they target. `docs/project-template/CHECKLIST.md` is the default; a project may extend it but should not weaken it.

## Standard command surface

Every project exposes the same three commands, regardless of what's underneath them, via a `Makefile` (or `justfile`) at the project's root:

- `setup` — install whatever the project needs to run
- `test` — run its test suite (or its review checklist, for non-code projects, as a script that exits non-zero on an unresolved item)
- `lint` — run its linters/formatters

This is what lets `.github/workflows/ci.yml` pick up a new project automatically: it looks for these targets rather than knowing anything about the project's stack.

For Python specifically — the default language for anything executable in this repository — [`docs/standards/python.md`](python.md) makes this concrete: which tools fill `lint` and `test`, what the `pyproject.toml` looks like, and a coverage floor CI enforces. [`docs/project-template/python-starter/`](../project-template/python-starter/) is a working skeleton that already satisfies it.

## Layout

**Code projects** follow a conventional layout:

```
<project-name>/
├── README.md       # filled in from docs/project-template/README.template.md
├── Makefile        # setup, test, lint
├── src/
├── tests/
└── docs/           # anything beyond what fits in the README
```

The internals of `src/` follow whatever is idiomatic for the language in use (`src/` + `pyproject.toml` and `pytest` for Python; `src/` + `package.json` and `vitest`/`jest` for TypeScript; and so on) — the standard here is the outer shape, not the inner one.

**Non-code deliverables** (a policy template, a governance framework, a set of encyclical-grounded talking points) use the same root shape minus `src/` and `tests/`:

```
<project-name>/
├── README.md
├── Makefile        # setup (if needed), test → runs the checklist, lint (if applicable)
├── docs/            # the deliverable itself, plus supporting material
└── CHECKLIST.md     # the review checklist this project is held to
```

## Reference frameworks

A project earns credibility with the audience it's written for by anchoring its recommendations in recognized standards, not just principle. Where relevant, map a project's guidance to:

- **NIST AI RMF** — the risk-management vocabulary most US institutions already use
- **ISO/IEC 42001** — the AI management-system standard institutions may already be certifying against
- **The EU AI Act's risk tiers** — for anything with a European or multinational audience

Catholic Social Teaching — subsidiarity, solidarity, the common good, the dignity of the human person — is the throughline every project in this repository is built on, and the standard by which the frameworks above are themselves judged, not merely cited alongside them. A project written for a secular audience still rests on this foundation; it simply argues from what the foundation implies, in terms that audience can act on, rather than from the foundation itself.
