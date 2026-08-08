# Contributing to cst-alignment-rubric

This project has two kinds of change, reviewed differently, per `CODEOWNERS`.

## Beta status

As of 2026-08-07, the theological-reviewer sign-off requirement below is **paused** for this project's beta phase — see the corresponding entry in `docs/theological-review-log.md`. This is a deliberate, temporary exception, not a retraction of the requirement: it exists specifically to keep the "who has interpretive authority" question from being quietly answered by whoever happens to write the code.

While paused:
- Content written into `principles/` or `rubric/` is **unreviewed**, and must say so plainly wherever it's presented — in the file itself and in anything (a README, a demo, a talk) that shows it to someone else.
- It is a working draft for iterating on shape and coverage during beta, not a working interpretation of CST in the sense the rest of this project's docs use that phrase.
- Before this project can claim `active` status (per `CHECKLIST.md`) or be presented as anything other than beta, the sign-off requirement must be reimposed: a named reviewer confirmed in `CODEOWNERS`, and everything written during beta reviewed retroactively and logged.

## Changing `principles/` or `rubric/`

Anything that changes what a principle means, how it's cited, what counts as a tension, or what a scenario tests requires sign-off from the named theological reviewer in `CODEOWNERS` — not just a technical maintainer's approval (suspended during beta; see above). This mirrors how a contract change needs a lawyer's sign-off, not an engineer's. Every such review gets a dated entry in `docs/theological-review-log.md`: what changed, who reviewed it, and what they said.

Citations must be checked against the primary source (*Magnifica Humanitas*, the Compendium of the Social Doctrine of the Church, the relevant encyclical) before a principle file merges — never reconstructed from memory or from a secondary summary.

## Changing `eval/` or `integrations/`

Ordinary code review applies: a technical maintainer's sign-off is sufficient. The eval harness follows [`../docs/standards/python.md`](../docs/standards/python.md) — tests written before or alongside the code, `make setup lint test` clean before a PR merges.

## Both

Follow [`../CONTRIBUTING.md`](../CONTRIBUTING.md)'s citation-integrity and tone rules: quote and cite primary sources accurately, write for a practitioner who has to actually govern an AI system, not for a reader being sold on the idea of governance.
