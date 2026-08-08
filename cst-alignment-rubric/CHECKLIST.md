# Go-live checklist

Extends [`../docs/project-template/CHECKLIST.md`](../docs/project-template/CHECKLIST.md) — every item there applies here too. This file adds what's specific to a rubric-and-harness project rather than weakening the default.

## Correctness (repo default)

- [ ] Tests pass (`make test`)
- [ ] Lint is clean (`make lint`)
- [ ] Every citation has been checked against its primary source, not reconstructed from memory

## Security & privacy (repo default)

- [ ] No secrets are committed anywhere in the project
- [ ] Dependencies are current and pinned deliberately, not floating
- [ ] Any CI access this project needs is scoped to the minimum required
- [ ] This project's work product does not touch real personal data — `eval/reports/` contains only genericized use descriptions or redacted prompt/response pairs, per the README's security & privacy section

## Fit for audience (repo default)

- [ ] The README's Audience and Grounding sections are filled in and specific
- [ ] The project reads like the work of a practitioner, not a generic AI-ethics essay
- [ ] Any bundled Skills validate cleanly and follow [`../docs/standards/skills.md`](../docs/standards/skills.md)

## Specific to this project

- [ ] All eight principle files exist under `principles/`, each with `id`, `magisterial_citations`, a plain-language `description`, and at least one entry in `tensions`
- [ ] `principles/non-negotiables.yaml` exists with `grounding` citations and at least the three current items (direct abortion, euthanasia/assisted suicide, direct killing of the innocent), reviewed for correct scope — not broader or narrower than what Compendium §155 and Magnifica Humanitas §55 actually name
- [ ] `rubric/known-tensions.md` documents at least three worked hard cases, including the preferential-option-vs-subsidiarity outreach-ranking case
- [ ] `CODEOWNERS` names a real theological reviewer — the `@TODO-theological-reviewer` placeholder has been replaced
- [ ] `docs/theological-review-log.md` has at least one dated, completed review entry
- [ ] `eval/assessment.py` and the `rate-ai-against-cst` skill run against at least one real described AI use and one real audited prompt/response pair — both the bright-line and graded paths, for both subjects — and produce a report artifact, not just a stub
- [ ] A dry run has been completed against 2–3 real use cases (StarRez agentic-AI work, or a diocesan/parish scenario), with results recorded
