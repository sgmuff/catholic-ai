# Contributing to cst-finding

This project has two kinds of change, reviewed differently, per `CODEOWNERS`.

## Beta status

Content written into `principles/` or `rubric/` is **unreviewed** by a named theological reviewer, and must say so plainly wherever it's presented — in the file itself and in anything (a README, a demo, a talk, or a generated report) that shows it to someone else. It is a working interpretation of CST for iterating on shape and coverage, not a canonical or magisterially-approved one.

As of 2026-08-08, this project does not gate `principles/` or `rubric/` changes on sign-off from a named theological reviewer (see `docs/theological-review-log.md`'s corresponding entry, and the retired requirement it replaces). Instead, the tool itself carries that caveat forward to whoever uses it: every generated report states plainly that it's unreviewed and recommends review by the using parish's own pastor or someone else there well versed in Catholic theology before a finding is acted on. That per-use review is the mechanism, not a one-time project-level sign-off.

## Changing `principles/` or `rubric/`

Ordinary technical review applies, the same as `eval/` or `integrations/` — see `CODEOWNERS`. What's different about this content isn't who signs off, it's the accuracy bar: anything that changes what a principle means, how it's cited, what counts as a tension, or what a scenario tests still gets a dated entry in `docs/theological-review-log.md` (what changed and why), so the reasoning behind the current content stays traceable even without a standing named reviewer.

Citations must be checked against the primary source (*Magnifica Humanitas*, the Compendium of the Social Doctrine of the Church, the relevant encyclical) before a principle file merges — never reconstructed from memory or from a secondary summary.

## Changing `eval/` or `integrations/`

Ordinary code review applies: a technical maintainer's sign-off is sufficient. The eval harness follows [`../docs/standards/python.md`](../docs/standards/python.md) — tests written before or alongside the code, `make setup lint test` clean before a PR merges.

## Both

Follow [`../CONTRIBUTING.md`](../CONTRIBUTING.md)'s citation-integrity and tone rules: quote and cite primary sources accurately, write for a practitioner who has to actually govern an AI system, not for a reader being sold on the idea of governance.
