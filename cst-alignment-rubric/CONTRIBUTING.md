# Contributing to cst-alignment-rubric

This project has two kinds of change, reviewed differently, per `CODEOWNERS`.

## Changing `principles/` or `rubric/`

Anything that changes what a principle means, how it's cited, what counts as a tension, or what a scenario tests requires sign-off from the named theological reviewer in `CODEOWNERS` — not just a technical maintainer's approval. This mirrors how a contract change needs a lawyer's sign-off, not an engineer's. Every such review gets a dated entry in `docs/theological-review-log.md`: what changed, who reviewed it, and what they said.

Citations must be checked against the primary source (*Magnifica Humanitas*, the Compendium of the Social Doctrine of the Church, the relevant encyclical) before a principle file merges — never reconstructed from memory or from a secondary summary.

## Changing `eval/` or `integrations/`

Ordinary code review applies: a technical maintainer's sign-off is sufficient. The eval harness follows [`../docs/standards/python.md`](../docs/standards/python.md) — tests written before or alongside the code, `make setup lint test` clean before a PR merges.

## Both

Follow [`../CONTRIBUTING.md`](../CONTRIBUTING.md)'s citation-integrity and tone rules: quote and cite primary sources accurately, write for a practitioner who has to actually govern an AI system, not for a reader being sold on the idea of governance.
