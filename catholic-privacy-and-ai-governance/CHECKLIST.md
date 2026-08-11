# Go-live checklist

Extends `docs/project-template/CHECKLIST.md`. A skill in this family doesn't ship
until every item here is checked or explicitly marked not applicable, with a
one-line reason.

## Correctness

- [x] Tests pass (`make test`) — 441 tests, 98% coverage
- [x] Lint is clean (`make lint`) — `ruff check`, `ruff format --check`, `mypy --strict`
- [x] Every citation — magisterial, CST, or a secular framework (GDPR, CCPA/CPRA,
      HIPAA, FERPA, ISO/IEC 27701, NIST Privacy Framework, NIST AI RMF,
      ISO/IEC 42001, EU AI Act) — has been checked against its primary source, not
      reconstructed from memory
      — **closed.** Every framework file was first checked against a
      primary or authoritative secondary source where one was reachable
      (GDPR against a mirror of the official text; HIPAA and FERPA
      against Cornell LII's CFR text; NIST's Privacy Framework against
      NIST's own published Core), each carrying its `source_url` for
      independent verification. A working review artifact covering all
      twelve frameworks was then published for the user's own pass at
      build sequence step 18; the user reviewed all twelve, across both
      domains, and confirmed them at build sequence step 19. Every
      `frameworks/*.yaml` file now reads `review_status: reviewed`.
      ISO/IEC 27701 and ISO/IEC 42001 remain the weakest cases on record
      — both paywalled commercial standards whose clause citations were
      authored from each standard's documented public structure rather
      than a fetch of the purchased text, and both files still say so
      directly — but the user's review addressed that caveat directly
      rather than this project silently dropping it once reviewed.

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
