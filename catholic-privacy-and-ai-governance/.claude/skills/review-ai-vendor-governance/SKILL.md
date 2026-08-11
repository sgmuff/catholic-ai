---
name: review-ai-vendor-governance
description: >
  Reviews a vendor's or foundation-model provider's AI governance
  documentation against a fixed seven-item baseline (model documentation,
  evaluation results, incident-notification commitment, upstream
  dependency disclosure, human-oversight support, model-update
  notification commitment, training-data governance) and the current
  framework registry. Marks each baseline item satisfied, partial, or
  missing with evidence or a gap, tracks remediation commitments, and
  states an overall risk level and reassessment date. Produces a report
  requiring AI-governance-lead or legal review before the vendor
  relationship proceeds or continues. Use when reviewing an AI vendor's
  or model provider's governance documentation against baseline
  requirements. Not for scoring a new AI system's own risk tier — use
  `assess-ai-system-risk-tier` for that instead.
---

# Review an AI vendor's governance documentation

Produces one advisory finding for one vendor: not a legal opinion, and not
a substitute for the AI-governance-lead or legal review it explicitly
requires before the relationship proceeds or continues.

This is the AI-governance domain's counterpart to
`review-vendor-privacy-assessment`, reusing that skill's shape directly
rather than designing a third one (build-plan.md step 16): a vendor
review isn't scored 1-5 on quality dimensions, and it isn't anchored to a
single event with a deadline — it's a fixed checklist, each item
independently marked `satisfied`, `partial`, or `missing` against what
the vendor's documentation actually shows, plus whatever remediation the
vendor has committed to and a date this review itself expires.

The judgment happens here, in conversation, grounded in this skill's own
bundled `references/baseline/ai-vendor.md` and `references/frameworks/`.
No API call, no separate rater. `scripts/review.py` only validates the
finished judgment against the real baseline items and framework ids, and
renders it; it never checks the vendor's documentation itself. Read the
actual baseline and framework content before marking anything — don't
score from memory of what a "typical model card" contains.

Every path below is written as `${CLAUDE_SKILL_DIR}/...`, a substitution
Claude Code resolves to this skill's own directory regardless of whether
it's installed inside a full checkout of the source project, as a plugin,
or standalone. If that substitution doesn't happen in your current
environment, resolve the same path relative to the folder containing this
`SKILL.md` instead.

## Architecture

Everything this skill reads or runs at review time lives inside its own
directory:

- `references/baseline/ai-vendor.md` — the seven-item checklist reviewed
  in step 2: how to mark status, and when `evidence`/`gap` are required.
- `references/frameworks/index.md` — the current framework registry, read
  in step 1 to decide which apply to this vendor relationship. Never
  hard-code a framework name anywhere in this procedure; read this file
  fresh every time, because the registry can grow or shrink independently
  of this `SKILL.md`.
- `references/frameworks/*/*.yaml` — the full content of every active
  framework: read the specific file(s) that apply in full so the
  `compliance` finding cites the exact provision each baseline item is
  grounded in, not a generic paraphrase.
- `references/review-schema.md` — the exact JSON shape step 4 writes.
- `scripts/review.py`, plus its sibling modules `baseline.py`,
  `language.py`, `concision.py`, `report.py` — the validate-and-render CLI
  step 4 calls. Dependency-free, stdlib-only Python (no `pyyaml`, no
  install step), so it runs with a plain `python3` wherever this skill
  ends up. Validates the written review against the real baseline item
  ids and framework ids in `references/`, enforces the compliance/CST
  language boundary, flags anything unusually long, and renders the
  Markdown report. Like its privacy-domain sibling, this bundle has a
  `baseline.py` copy instead of `rubric.py` — there's no rubric here to
  parse.

This bundle is generated, not hand-edited, except for `scripts/review.py`
itself and this file. In the source project
([sgmuff/catholic-ai](https://github.com/sgmuff/catholic-ai)), the rest is
synced from the authored `baselines/` and `frameworks/` directories by
`eval/sync_skill_bundle.py`; a test fails that project's CI if the bundle
ever drifts from what that script would produce. If you're working in that
project and just changed `baselines/` or `frameworks/`, re-run the sync
before testing this skill — the bundle above, not the source directories,
is what actually gets read here.

## 1. Intake the vendor and identify applicable frameworks

Ask what the vendor's system or model does, what institutional data or
decisions it touches, and what documentation is available to review (a
model card, technical documentation, evaluation results, a contract's AI
provisions...). Read
`${CLAUDE_SKILL_DIR}/references/frameworks/index.md` in full. For each
entry, ask or infer whether it applies (a vendor supplying a high-risk AI
system under the EU AI Act's Annex III categories, in scope of the Act's
territorial reach → EU AI Act; an institution that has adopted the NIST
AI RMF to structure its own vendor diligence → NIST AI RMF). Read the
specific file(s) that apply in full. Record every framework considered in
`frameworks_considered`, including ones ruled inapplicable, so the record
shows the reasoning happened rather than being skipped.

## 2. Check the vendor's documentation against the baseline

Read `${CLAUDE_SKILL_DIR}/references/baseline/ai-vendor.md` in full — all
seven items and the shared reviewing instructions at the top. For each
item:

- Mark `satisfied` only when the documentation directly evidences it;
  `partial` when something exists but falls short (e.g. a model card
  exists but omits known limitations); `missing` when nothing was found.
- Write `evidence` for `satisfied` or `partial` — the specific document
  or artifact, not a restatement of the item.
- Write `gap` for `partial` or `missing` — the specific thing still
  needed, concrete enough that the vendor could act on it directly.
- Check what the documentation actually shows, not what a reputable
  vendor would probably have.

## 3. Record remediation, reassessment, and overall risk

For each gap the vendor has already committed to closing, record it in
`remediation_commitments` with the vendor's own stated target date and
`status: open`. Set `reassessment_due` — when this vendor needs to be
checked again, sooner than the institution's default cadence if a
material gap or a near-term commitment warrants it, and always sooner
than usual after any known model update. Assess `overall_risk` — `low`,
`moderate`, `high`, or `critical` — from the baseline results as a whole:
how many items are unmet, how consequential the system's decisions are,
and whether open remediation with a credible date offsets an unmet item
or not.

## 4. Write and render the record

Write a JSON file matching
`${CLAUDE_SKILL_DIR}/references/review-schema.md` exactly, then run:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/review.py --input <path-to-json> --out-dir <reports-dir>
```

`<reports-dir>` is `reports/` created next to wherever you're working in
this conversation, unless the user asks for somewhere else.

The script validates before it renders: every baseline item present
exactly once, every framework id real, `evidence` present whenever a
status requires it, `gap` present whenever a status requires it, every
remediation commitment has a real target date, and — enforcing this
project's own hard rule on Catholic language — the `compliance` field
rejected if any Catholic Social Teaching vocabulary has leaked into it. A
non-zero exit with "Could not build review" on stderr lists every problem
found; fix the JSON and rerun rather than working around the validation.
A zero exit may still print non-fatal warnings on stderr about a field
running long — reread the flagged parts for restated or padded text
before treating the report as final.

## 5. Report back in plain language, briefly

This is an advisory draft, grounded in a working interpretation of the
frameworks actually applied above — not a legal opinion — and it requires
AI-governance-lead or legal review before the vendor relationship
proceeds or continues. State the overall risk level plainly and up front,
then the specific unmet items and any open remediation with its date.
This is a summary, not a restatement of the full report. Close by
pointing the user to the rendered report file for the full basis on every
item.

## Human oversight and escalation

This skill never approves or terminates a vendor relationship on anyone's
behalf, and never represents a remediation commitment as fulfilled until
evidence of completion is actually reviewed — it drafts a finding for a
named accountable person to review and act on. Escalate plainly, rather
than only noting in the report, an overall risk assessed `high` or
`critical`, or a vendor supplying a high-risk AI system with any baseline
item marked `missing`.

## Grounding

Personalism and the dignity of the human person ground why relying on a
vendor's AI system doesn't dissolve the institution's own responsibility
for decisions it makes about people using that system. The primacy of
human judgment over automated determination grounds why the
human-oversight-support item matters as much as any technical
capability. Subsidiarity keeps oversight of the vendor relationship
active rather than delegated away unexamined once a contract is signed.
Solidarity weighs toward closing a gap rather than accepting residual
risk when the system's decisions affect those least able to contest them.
This reasoning belongs in `cst_reflection`, alongside the compliance
findings, never inside them.
