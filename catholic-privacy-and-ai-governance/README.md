# Catholic Privacy and AI Governance

Turns privacy and AI-governance judgment-and-drafting duties — impact assessments,
risk classifications, documentation, triage — into a family of standalone Claude
Skills, with compliance content written exactly as a regulator or plaintiff's
counsel would expect it.

## Audience

Any institution that processes personal data or builds, deploys, or procures AI
systems — a diocese, a Catholic hospital system, a university, a parish, or a
secular company. The work product (a DPIA, an AI risk-tier classification, model
documentation) is usable by a DPO, general counsel, or AI governance lead
regardless of whether they share the theology grounding it.

## Status

`draft` — held there for one specific, deliberate reason, not because
nothing works yet. Six skills are built, tested, and validated
end-to-end: a router (`catholic-privacy-and-ai-governance`); one flagship
per domain — `draft-privacy-impact-assessment` (privacy, nine frameworks:
GDPR DPIA, GDPR data-subject rights, GDPR breach notification, CCPA/CPRA,
California's breach notification law, HIPAA, FERPA, ISO/IEC 27701, NIST
Privacy Framework) and `assess-ai-system-risk-tier` (AI governance, two
frameworks: the EU AI Act, NIST AI RMF), proving the pluggable
architecture generalizes across domains, not just across frameworks
within one; `draft-privacy-notice-update`, proving a second skill can
share a domain and a rubric with its sibling with zero special-casing;
`triage-privacy-rights-request`, proving a non-rubric-scored task shape
(classification, a single calculated deadline, a gap checklist) fits the
same architecture without forcing it into the rubric-scored shape the
other skills use; and `triage-privacy-incident`, a sibling shape proving
that a task with several independent, simultaneous obligations (a breach
notification owed to a regulator *and* affected individuals *and*
possibly other parties, each with its own deadline) doesn't force-fit
into the single-deadline shape either — it gets its own. What's not done:
every framework file in `frameworks/` is marked `review_status:
unreviewed` — citations were checked against a primary or authoritative
secondary source where one was reachable, never reconstructed from
memory, but none has been checked by someone with actual legal or
standards expertise in that specific framework. `CHECKLIST.md` tracks
this as the project's one open go-live item; status moves to `active`
once it closes, not once more gets built. See
[`build-plan.md`](build-plan.md)'s build sequence for what's done and
what's next — six more skills are planned across both domains.

## Grounding

Personalism and the dignity of the human person ground informational
self-determination: a person's data is an extension of the person, not a resource
to optimize. Subsidiarity keeps data-handling and AI-oversight decisions as close
as possible to the person concerned; solidarity protects those least able to
contest how their data or an AI system's decision about them is used.
*Magnifica Humanitas*'s claim about the primacy of human judgment over automated
determination grounds this project's human-oversight requirements directly, in
both domains.

Recognized secular frameworks anchor the compliance side: GDPR, CCPA/CPRA,
California's breach notification law, HIPAA, FERPA, ISO/IEC 27701, and the
NIST Privacy Framework for privacy; the EU AI Act's risk tiers and NIST AI
RMF for AI governance (ISO/IEC 42001 not yet registered). These are
registered in a pluggable `frameworks/` registry rather
than fixed in code, so the set can grow or shrink without restructuring
anything (`build-plan.md` §3) — and a whole second domain was added to that
same registry without touching the shared validation or rendering code at all
(`build-plan.md` step 11).

Catholic language is never a substitute for compliance language: every report this
project produces keeps regulatory findings in exact regulatory register, with
Catholic Social Teaching grounding layered alongside it, never in place of it
(`build-plan.md` §2.1).

## Stack

Python 3.12, `src/` layout, one runtime dependency (`pyyaml`) for this
project's own dev-time tooling — loading and validating the framework
registry, rendering each skill's bundle. What actually runs once a skill is
installed is different on purpose: each skill's own `scripts/` is a
separate, dependency-free stdlib-only copy, per
[`docs/standards/skills.md`](../docs/standards/skills.md)'s
standalone-distribution requirement — proven, not just asserted, by running
both `draft-privacy-impact-assessment`'s and `assess-ai-system-risk-tier`'s
scripts with a bare Python interpreter that has no packages installed at
all. Both skills' `scripts/assessment.py` are structurally identical code
(only the module docstring differs) — the same file works unchanged in
either skill because it discovers its own bundled rubric file by name
rather than hard-coding one.

## Setup

```
make setup
```

Requires Python 3.12+; if your default `python3` resolves to an older
interpreter, create the venv with a 3.12 binary directly (e.g.
`python3.12 -m venv .venv`) before the rest of `make setup`.

## Testing

```
make test
```

238 tests, 98% coverage. `make lint` runs `ruff check`, `ruff format --check`,
and `mypy --strict`. `make check-framework-freshness` flags any framework
entry due for a periodic review; `make sync-skill-bundle` regenerates every
skill's bundled `references/` and `scripts/` from this project's authored
source. `agentskills validate` (the CLI the `skills-ref` package installs)
passes for every skill in the family.

## Security & privacy notes

Every fixture and example used in tests, and every scenario used to dry-run
the flagship skill, is fabricated — no real person's data and no real
institution's actual deployed system, ever. Framework citations are drawn
from a primary or authoritative secondary legal source where one was
reachable (see each file's `source_url`), never invented to fill a gap —
and every framework file says plainly, via `review_status: unreviewed`,
that it hasn't yet been checked by a domain expert, rather than implicitly
claiming verification it doesn't have (see Status, above). This project's
own work product exists specifically to make institutions address data
minimization, lawful basis, retention, and human oversight for their own
processing and AI systems — see `rubric/criteria.md` (privacy) and
`rubric/ai-criteria.md` (AI governance) for how. Compliance-
language integrity is structurally enforced, not just stated: every
generated report's `compliance` section is validated against a blocklist
that rejects Catholic Social Teaching vocabulary bleeding into regulatory
findings (`build-plan.md` §2.1).

## Skills used or provided

Six skills, all validated with `agentskills validate` and installable via
this repo's root `.claude-plugin/marketplace.json`:

- `catholic-privacy-and-ai-governance` — the router; routes a generic
  privacy or AI-governance request to the right specialist skill rather
  than performing any assessment itself.
- `draft-privacy-impact-assessment` — the privacy-domain flagship; drafts a
  DPIA against the current framework registry and a seven-dimension
  privacy-by-design rubric.
- `assess-ai-system-risk-tier` — the AI-governance-domain flagship;
  classifies an AI system against the EU AI Act's risk tiers and NIST AI
  RMF's functions, then scores it against a seven-dimension AI-governance
  rubric.
- `draft-privacy-notice-update` — drafts a proposed privacy notice or
  policy revision for a changed practice, grounded in the same rubric and
  framework registry `draft-privacy-impact-assessment` uses.
- `triage-privacy-rights-request` — triages an incoming data-subject
  rights request against the current framework registry, calculates the
  governing response deadline, and flags outstanding gaps before a
  response is sent. No rubric — a different task shape (classification,
  a single deadline, gaps) from its sibling skills above.
- `triage-privacy-incident` — triages a reported privacy incident or
  possible breach, scores its severity, and identifies every independent
  notification obligation this incident triggers — to a regulator,
  affected individuals, or others — each with its own deadline, rather
  than a single governing one. No rubric.

Six more are planned across both domains — see `family-manifest.yaml`
and `build-plan.md` §8 for the full list.
