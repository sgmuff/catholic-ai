---
name: review-ai-system-reassessment
description: >
  Checks one inventoried AI system against the current framework registry
  and its own defined re-evaluation interval, and produces a single
  verdict — current, needs review, needs a documentation update, or
  retire — with a target date whenever action is needed. Produces a
  report that requires an AI-governance lead or legal review before the
  system is acted on. Use when checking whether an inventoried AI
  system is overdue for reassessment, its documentation needs updating,
  or it remains current. Not for classifying a new AI system's risk tier
  — use assess-ai-system-risk-tier for that instead.
---

# Check an AI system for overdue reassessment

Produces one advisory verdict for one inventoried AI system: not a legal
opinion, and not a substitute for the AI-governance-lead or legal review
it explicitly requires before the system is acted on.

This is the AI-governance domain's counterpart to
`review-data-retention-entry`, reusing that skill's shape directly rather
than designing a third one (build-plan.md step 18): one system, checked
once, against its own defined re-evaluation interval, producing one
verdict — `current`, `needs-review`, `needs-update`, or `retire` — not a
score, not a list of deadlines, not a checklist. Don't pad the record
with structure this task doesn't need.

The judgment happens here, in conversation, grounded in this skill's own
bundled `references/frameworks/`. No API call, no separate rater.
`scripts/retention.py` only validates the finished judgment against the
real framework ids and internal date logic, and renders it; it never
decides the verdict itself. Read the actual framework content before
determining applicability — don't reason from memory of what a framework
"usually" requires.

Every path below is written as `${CLAUDE_SKILL_DIR}/...`, a substitution
Claude Code resolves to this skill's own directory regardless of whether
it's installed inside a full checkout of the source project, as a plugin,
or standalone. If that substitution doesn't happen in your current
environment, resolve the same path relative to the folder containing this
`SKILL.md` instead.

## Architecture

Everything this skill reads or runs at review time lives inside its own
directory:

- `references/frameworks/index.md` — the current framework registry, read
  in step 1 to decide which apply to this system. Never hard-code a
  framework name anywhere in this procedure; read this file fresh every
  time, because the registry can grow or shrink independently of this
  `SKILL.md`.
- `references/frameworks/*/*.yaml` — the full content of every active
  framework: read the specific file(s) that apply in full before
  reasoning about whether the system's current assessment is still
  current.
- `references/retention-schema.md` — the exact JSON shape step 3 writes.
- `scripts/retention.py`, plus its sibling modules `language.py`,
  `concision.py`, `report.py` — the validate-and-render CLI step 3 calls.
  Dependency-free, stdlib-only Python (no `pyyaml`, no install step), so
  it runs with a plain `python3` wherever this skill ends up. Validates
  the written entry against the real framework ids in `references/`,
  enforces the compliance/CST language boundary, flags anything unusually
  long, and renders the Markdown report. No `rubric.py`, no
  `baseline.py` — this shape uses neither.

This bundle is generated, not hand-edited, except for
`scripts/retention.py` itself and this file. In the source project
([sgmuff/catholic-ai](https://github.com/sgmuff/catholic-ai)), the rest is
synced from the authored `frameworks/` directory by
`eval/sync_skill_bundle.py`; a test fails that project's CI if the bundle
ever drifts from what that script would produce. If you're working in
that project and just changed `frameworks/`, re-run the sync before
testing this skill — the bundle above, not the source directory, is what
actually gets read here.

## 1. Intake the system and identify applicable frameworks

Ask what this AI system is, its purpose, its risk tier (which sets its
own re-evaluation interval — a high-risk system needs more frequent
reassessment than a minimal-risk one), and when it was last assessed. If
the system is vendor-supplied and its provider has published updated
documentation or a new model card since the last assessment, offer to find
and cite it — that's often exactly what triggers a `needs-update` verdict
below — confirmed by the user before it's relied on (build-plan.md §2.4).
Read `${CLAUDE_SKILL_DIR}/references/frameworks/index.md` in full, and
read the specific file(s) that apply — the EU AI Act's obligations and
NIST AI RMF's MEASURE/MANAGE functions both bear directly on whether a
system's current documentation and evaluation results still hold.
Record every framework considered in `frameworks_considered`, including
ones ruled inapplicable.

## 2. Reach a verdict

Compare the system's `last_reviewed_date` against its own defined
re-evaluation interval:

- **`current`** — the interval hasn't lapsed and the system's
  documentation and evaluation results still hold; no action needed, no
  `target_date` required.
- **`needs-review`** — the interval has lapsed; someone needs to actually
  re-run the evaluation, not just re-confirm the old one.
- **`needs-update`** — the underlying system hasn't materially changed
  but its documentation is stale or incomplete relative to what it
  actually does now.
- **`retire`** — the system should be decommissioned rather than
  reassessed again (superseded, no longer serving its stated purpose, or
  a risk that reassessment alone can't address).

Every action other than `current` requires a `target_date` — a real date
by which the action should happen, not an open-ended "soon." Write a
rationale grounded in the specific facts (the interval, the last-reviewed
date, the arithmetic between them), not a restatement of the action name.

## 3. Write and render the record

Write a JSON file matching
`${CLAUDE_SKILL_DIR}/references/retention-schema.md` exactly, then run:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/retention.py --input <path-to-json> --out-dir <reports-dir>
```

`<reports-dir>` is `reports/` created next to wherever you're working in
this conversation, unless the user asks for somewhere else.

The script validates before it renders: every framework id real,
`verdict.action` one of the four defined values, a `target_date` present
whenever the action requires one, and — enforcing this project's own hard
rule on Catholic language — the `compliance` field rejected if any
Catholic Social Teaching vocabulary has leaked into it. A non-zero exit
with "Could not build reassessment entry" on stderr lists every problem
found; fix the JSON and rerun rather than working around the validation.
A zero exit may still print non-fatal warnings on stderr about a field
running long — reread the flagged parts for restated or padded text
before treating the report as final.

## 4. Report back in plain language, briefly

This is an advisory draft, grounded in a working interpretation of the
frameworks actually applied above — not a legal opinion — and it requires
an AI-governance lead or legal review before the system is acted on.
State the verdict and target date (if any) plainly and up front. This is
a summary, not a restatement of the full report. Close by pointing the
user to the rendered report file for the full basis.

## Human oversight and escalation

This skill never decommissions a system or approves its continued use on
anyone's behalf, and never makes a final determination that a system's
documentation is sufficient — it drafts a finding for a named accountable
person to review and act on. Escalate plainly, rather than only noting in
the report, a `retire` verdict for a high-risk system, or any verdict on
a system that makes or materially informs a consequential decision about
a person.

## Grounding

Personalism and the dignity of the human person (Catechism §§356-357, 1700)
ground why a system whose documentation has gone stale is a quiet harm even
when nothing else goes wrong with it — a system a person's outcome depends
on is owed active, current oversight, not a one-time assessment treated as
permanent. The primacy of human judgment over automated determination
(*Antiqua et Nova*, DDF & Dicastery for Culture and Education, 28 Jan. 2025,
§44) grounds why a lapsed interval gets flagged rather than silently
assumed still valid. Full citations: build-plan.md §2.3. This reasoning
belongs in `cst_reflection`, alongside the compliance findings, never
inside them.
