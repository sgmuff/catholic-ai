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

`active`. All thirteen skills across both domains are built, tested, and
validated end-to-end — the full backlog from `build-plan.md` §8, minus
one (`draft-ai-risk-impact-assessment`) retired as a duplicate of an
already-built skill. Together they cover six distinct task shapes:
rubric-scored assessment (`draft-privacy-impact-assessment`,
`assess-ai-system-risk-tier`, `draft-privacy-notice-update`,
`draft-model-card`), single-governing-deadline triage
(`triage-privacy-rights-request`), parallel-obligation incident response
(`triage-privacy-incident`, `triage-ai-incident`), per-item baseline
review (`review-vendor-privacy-assessment`, `review-ai-vendor-governance`),
single-verdict retention/reassessment (`review-data-retention-entry`,
`review-ai-system-reassessment`), and registry-impact regulatory-change
mapping (`map-regulatory-change`, `map-ai-regulatory-change`) — plus the
router. Every shape but the first was proven to generalize across both
domains at effectively zero marginal cost: the validation and rendering
logic is reused unchanged, only a module docstring and an argparse
description differ, confirmed by an `ast`-normalized structural-identity
test for each pair. Twelve frameworks are registered (GDPR DPIA, GDPR
data-subject rights, GDPR breach notification, CCPA/CPRA, California's
breach notification law, HIPAA, FERPA, ISO/IEC 27701, NIST Privacy
Framework for privacy; the EU AI Act, NIST AI RMF, ISO/IEC 42001 for AI
governance), and every one now carries `review_status: reviewed` — the
project's DPO reviewed all twelve, across both domains, against the
review artifact `build-plan.md` step 18 published. See
[`build-plan.md`](build-plan.md)'s build sequence for the full history of
how each shape was designed and where it generalized, and
[`CHECKLIST.md`](CHECKLIST.md) for the closed go-live checklist.

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
NIST Privacy Framework for privacy; the EU AI Act's risk tiers, NIST AI
RMF, and ISO/IEC 42001 for AI governance. These are
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

441 tests, 98% coverage. `make lint` runs `ruff check`, `ruff format --check`,
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
reachable (see each file's `source_url`), never invented to fill a gap,
and every framework file now carries `review_status: reviewed` — checked
by the project's own DPO, not merely against a primary source by the
agent that authored it (see Status, above). This project's own work
product exists specifically to make institutions address data
minimization, lawful basis, retention, and human oversight for their own
processing and AI systems — see `rubric/criteria.md` (privacy) and
`rubric/ai-criteria.md` (AI governance) for how. Compliance-
language integrity is structurally enforced, not just stated: every
generated report's `compliance` section is validated against a blocklist
that rejects Catholic Social Teaching vocabulary bleeding into regulatory
findings (`build-plan.md` §2.1).

## Skills used or provided

Thirteen skills, all validated with `agentskills validate` and installable
via this repo's root `.claude-plugin/marketplace.json`:

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
- `triage-ai-incident` — the AI-governance sibling of
  `triage-privacy-incident`, reusing the same incident shape unchanged:
  triages a reported AI safety, bias, or reliability incident, scores its
  severity, and identifies every independent notification or reporting
  obligation it triggers — to a market surveillance authority, an
  internal governance body, or others. No rubric.
- `review-vendor-privacy-assessment` — reviews a vendor's privacy
  questionnaire, DPA, or certifications against a fixed eight-item
  baseline, marking each item satisfied, partial, or missing with
  evidence or a gap, tracking remediation commitments, and stating an
  overall risk level and reassessment date. No rubric — a fourth task
  shape (a per-item baseline check) from its sibling skills above.
- `review-ai-vendor-governance` — the AI-governance sibling of
  `review-vendor-privacy-assessment`, reusing the same review shape
  unchanged against a seven-item AI-vendor baseline (model documentation,
  evaluation results, incident-notification commitment, upstream
  dependency disclosure, human-oversight support, model-update
  notification, training-data governance).
- `draft-model-card` — produces a model/system documentation record for
  an AI system, grounded in the same rubric and framework registry
  `assess-ai-system-risk-tier` uses, the way `draft-privacy-notice-update`
  shares `draft-privacy-impact-assessment`'s.
- `review-data-retention-entry` — checks one data-inventory entry against
  the current framework registry and its own stated review interval, and
  produces a single verdict — `current`, `needs-review`, `needs-update`,
  or `retire` — with a target date when action is needed. No rubric — the
  smallest task shape in the family, deliberately: one entry, one
  verdict, no score, no deadline list, no checklist.
- `review-ai-system-reassessment` — the AI-governance sibling of
  `review-data-retention-entry`, reusing the same shape unchanged for one
  inventoried AI system checked against its own defined re-evaluation
  interval.
- `map-regulatory-change` — given a pasted privacy regulatory or
  standards development, summarizes it and maps its impact against the
  framework registry itself, recommending whether to register, update,
  retire, or take no action on a framework entry. The only skill in this
  family that doesn't evaluate an institution's own activity, system,
  vendor, or entry — it evaluates this project's own registry.
- `map-ai-regulatory-change` — the AI-governance sibling of
  `map-regulatory-change`, reusing the same shape unchanged.

`draft-ai-risk-impact-assessment` is retired, not planned — as originally
scoped it would have duplicated `assess-ai-system-risk-tier`'s already-
built full rubric-scored assessment. The backlog in `family-manifest.yaml`
and `build-plan.md` §8 is otherwise complete.
