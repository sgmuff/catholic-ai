---
name: review-data-retention-entry
description: >
  Checks one data-inventory entry against the current framework registry
  and its own stated review interval, and produces a single verdict —
  current, needs review, needs an updated retention justification, or
  retire — with a target date whenever action is needed. Produces a
  report that requires DPO or legal review before the entry is acted on.
  Use when checking whether a specific data-inventory entry's retention
  is still justified, or whether it's overdue for review, an updated
  justification, or deletion. Not for a full processing activity
  assessment — use draft-privacy-impact-assessment for that instead.
---

# Check a data-retention entry

Produces one advisory verdict for one inventory entry: not a legal
opinion, and not a substitute for the DPO or legal review it explicitly
requires before the entry is acted on.

This is the smallest task shape in this family, deliberately
(build-plan.md step 18): one entry, checked once, against its own stated
review interval, producing one verdict — `current`, `needs-review`,
`needs-update`, or `retire` — not a score, not a list of deadlines, not a
checklist. Don't pad the record with structure this task doesn't need.

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
  in step 1 to decide which laws apply to this entry. Never hard-code a
  framework name anywhere in this procedure; read this file fresh every
  time, because the registry can grow or shrink independently of this
  `SKILL.md`.
- `references/frameworks/*/*.yaml` — the full content of every active
  framework: read the specific file(s) that apply in full before
  reasoning about whether the retention is still justified.
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

## 1. Intake the entry and identify applicable frameworks

Ask what this data-inventory entry covers: what it is, its purpose, and
what retention interval currently applies to it (a stated policy, a
regulatory maximum, or "until the relationship ends" — whatever's
actually on record) and when it was last reviewed. What the entry actually
is and why it's kept is internal information only the user has; if the
applicable regulatory maximum itself needs checking against the source
text rather than what's on record, that's already covered by the framework
lookup below rather than a separate search (build-plan.md §2.4). Read
`${CLAUDE_SKILL_DIR}/references/frameworks/index.md` in full, and read
the specific file(s) that apply — most frameworks in this registry state
their own retention-adjacent requirement (data minimization, storage
limitation) worth grounding the verdict in. Record every framework
considered in `frameworks_considered`, including ones ruled inapplicable.

## 2. Reach a verdict

Compare the entry's `last_reviewed_date` against its own stated review
interval:

- **`current`** — the interval hasn't lapsed and the stated purpose still
  holds; no action needed, no `target_date` required.
- **`needs-review`** — the interval has lapsed but the underlying purpose
  may still be valid; someone needs to actively re-confirm it.
- **`needs-update`** — the retention justification itself is stale or
  incomplete (e.g. a policy changed, or the original justification never
  named a concrete interval); it needs to be rewritten, not just
  re-confirmed.
- **`retire`** — the stated purpose no longer applies; the entry should
  be deleted (a data element) or decommissioned (a system) rather than
  reviewed again.

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
with "Could not build retention entry" on stderr lists every problem
found; fix the JSON and rerun rather than working around the validation.
A zero exit may still print non-fatal warnings on stderr about a field
running long — reread the flagged parts for restated or padded text
before treating the report as final.

## 4. Report back in plain language, briefly

This is an advisory draft, grounded in a working interpretation of the
frameworks actually applied above — not a legal opinion — and it requires
DPO or legal review before the entry is acted on. State the verdict and
target date (if any) plainly and up front. This is a summary, not a
restatement of the full report. Close by pointing the user to the
rendered report file for the full basis.

## Human oversight and escalation

This skill never deletes data or decommissions a system on anyone's
behalf, and never makes a final determination that a retention
justification is sufficient — it drafts a finding for a named accountable
person to review and act on. Escalate plainly, rather than only noting in
the report, a `retire` verdict involving special-category or otherwise
high-sensitivity data, since that determination should not sit
unreviewed until its own target date arrives.

## Grounding

Personalism and the dignity of the human person (Catechism §§356-357, 1700)
ground why data kept without an active justification is a quiet harm even
when nothing else goes wrong with it — a person's data outliving its
purpose treats convenience as sufficient reason to keep something that was
only ever justified by a specific need. Subsidiarity (Compendium of the
Social Doctrine of the Church §§185-187) keeps the retention decision close
to an active, reviewable justification rather than defaulting to indefinite
storage. Full citations: build-plan.md §2.3. This reasoning belongs in
`cst_reflection`, alongside the compliance findings, never inside them.
