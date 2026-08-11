# Go-live checklist

Extends `docs/project-template/CHECKLIST.md`. A skill in this family doesn't ship
until every item here is checked or explicitly marked not applicable, with a
one-line reason.

## Correctness

- [x] Tests pass (`make test`) — 335 tests, 98% coverage
- [x] Lint is clean (`make lint`) — `ruff check`, `ruff format --check`, `mypy --strict`
- [ ] Every citation — magisterial, CST, or a secular framework (GDPR, CCPA/CPRA,
      HIPAA, FERPA, ISO/IEC 27701, NIST Privacy Framework, NIST AI RMF,
      ISO/IEC 42001, EU AI Act) — has been checked against its primary source, not
      reconstructed from memory
      — **not yet.** Every framework file (`frameworks/*/*.yaml`) was checked
      against a primary or authoritative secondary source where one was
      reachable (GDPR against a mirror of the official text; HIPAA and
      FERPA against Cornell LII's CFR text; NIST's Privacy Framework
      against NIST's own published Core) and each carries its `source_url`
      for independent verification — but none has been checked by someone
      with actual legal or standards expertise in that specific framework.
      ISO/IEC 27701 is the weakest case: it's a paywalled commercial
      standard, so its clause citations are authored from the standard's
      documented public structure, not a fetch of the purchased text, and
      its file says so directly. This is the one item this project's
      status stays `draft` for — see README's Status section. **This is
      not "not applicable"; it is open.**

## Security & privacy

- [x] No secrets are committed anywhere in the project
- [x] Dependencies are current and pinned deliberately, not floating —
      matches `docs/standards/python.md`'s own `pyproject.toml` shape
- [x] Any CI access this project needs is scoped to the minimum required —
      not applicable: no project-specific CI workflow has been added: this
      project is picked up by the repo-wide `ci.yml` via the standard
      `setup`/`lint`/`test` targets, with no elevated access requested
- [x] Data minimization, lawful basis, retention, and human oversight of
      consequential decisions are each addressed in the README's security &
      privacy section

## This project's own hard rules (`build-plan.md` §2)

- [x] **§2.1 — compliance/CST separation:** a sampled report's `compliance`
      section is free of CST vocabulary (`tests/test_language.py` and
      `tests/test_assessment.py`'s `TestValidateAssessmentComplianceBoundary`
      pass, and a manual read of all three build-plan.md §8 dry-run reports
      confirmed it)
- [x] **§2.2 — concision:** a sampled report reads as tight, not merely correct —
      no restated rubric text, no repeated boilerplate, no padding around a
      required finding — confirmed by eye on the same three dry-run reports;
      none tripped the concision lint either

## Pluggable frameworks (`build-plan.md` §3)

- [x] Every `active` entry in `frameworks/index.yaml` has a matching file that
      validates against `frameworks/schema.yaml`
- [x] `make check-framework-freshness` has been run and any stale entry
      reviewed — none stale as of this run
- [x] Adding or retiring a framework was tested end-to-end without editing any
      skill's `SKILL.md` — confirmed across five separate framework additions
      within the privacy domain, and again adding an entire second domain
      (AI governance) without touching any shared validation or rendering
      code, only `frameworks/`, `rubric/`, `family-manifest.yaml`, and one
      new `SKILL.md` (`build-plan.md` step 11)

## Fit for audience

- [x] The README's Audience and Grounding sections are filled in and specific —
      not a placeholder
- [x] The project reads like the work of a practitioner addressing its stated
      audience, not a generic AI-ethics essay
- [x] Every skill in the family, including the router, validates cleanly
      (`agentskills validate` — the CLI the `skills-ref` package installs) and
      follows [`docs/standards/skills.md`](../docs/standards/skills.md)
