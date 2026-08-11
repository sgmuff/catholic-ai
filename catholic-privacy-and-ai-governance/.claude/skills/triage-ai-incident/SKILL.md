---
name: triage-ai-incident
description: >
  Triages a reported AI safety, bias, or reliability incident — a safety
  failure, a harmful or biased output, a hallucination causing material
  reliance harm, or a system behaving outside its documented scope —
  against the current framework registry (EU AI Act Art. 73 serious-
  incident reporting, NIST AI RMF). Identifies which frameworks apply,
  scores severity, identifies every independent notification or reporting
  obligation this incident triggers — to a market surveillance authority,
  an internal governance body, or others, each with its own deadline —
  flags outstanding gaps, and states whether it meets the escalation
  threshold. Produces a report requiring AI-governance-lead or legal
  review before any notification is sent. Use when a possible AI safety,
  bias, or reliability incident needs its severity, notification
  obligations, and escalation worked out. Not for a privacy incident with
  no AI system involved — use `triage-privacy-incident` for that instead.
---

# Triage an AI incident

Produces one advisory finding for one reported incident: not a legal
opinion, and not a substitute for the AI-governance-lead or legal review
it explicitly requires before any notification is sent or the incident is
closed.

This is the AI-governance domain's counterpart to
`triage-privacy-incident`, reusing that skill's shape directly rather than
designing a third one (build-plan.md step 15): an AI incident, like a
privacy incident, can trigger several **independent, simultaneous**
notification obligations to different audiences at once — a market
surveillance authority under the EU AI Act's severity-tiered deadlines, an
internal governance body under an adopted NIST AI RMF profile — none of
which "governs" over the others. `notification_obligations` below is a
list for exactly that reason, not a single deadline field.

The judgment happens here, in conversation, grounded in this skill's own
bundled `references/frameworks/`. No API call, no separate rater.
`scripts/incident.py` only validates the finished judgment against the
real framework ids and internal date logic, and renders it; it never
assesses severity or calculates anything itself. Read the actual
framework content before determining applicability, severity, or a
deadline — don't reason from memory of what a framework "usually"
requires.

Every path below is written as `${CLAUDE_SKILL_DIR}/...`, a substitution
Claude Code resolves to this skill's own directory regardless of whether
it's installed inside a full checkout of the source project, as a plugin,
or standalone. If that substitution doesn't happen in your current
environment, resolve the same path relative to the folder containing this
`SKILL.md` instead.

## Architecture

Everything this skill reads or runs at triage time lives inside its own
directory:

- `references/frameworks/index.md` — the current framework registry, read
  in step 1 to decide which apply. Never hard-code a framework name
  anywhere in this procedure; read this file fresh every time, because the
  registry can grow or shrink independently of this `SKILL.md`.
- `references/frameworks/*/*.yaml` — the full content of every active
  framework: its trigger, required elements (including the EU AI Act's
  severity-tiered reporting deadlines), and terms of art. Read the
  specific file(s) that apply in full before determining applicability,
  severity, or a deadline — never work from memory of what a framework
  "usually" requires.
- `references/incident-schema.md` — the exact JSON shape step 4 writes.
- `scripts/incident.py`, plus its sibling modules `language.py`,
  `concision.py`, `report.py` — the validate-and-render CLI step 4 calls.
  Dependency-free, stdlib-only Python (no `pyyaml`, no install step), so it
  runs with a plain `python3` wherever this skill ends up. Validates the
  written incident record against the real framework ids in `references/`,
  checks every notification obligation's deadline against the discovery
  date, enforces the compliance/CST language boundary, flags anything
  unusually long, and renders the Markdown report. Like its sibling
  `triage-privacy-incident`, this bundle has no `rubric.py` and no
  `references/rubric/` — there's no rubric here to parse.

This bundle is generated, not hand-edited, except for `scripts/incident.py`
itself and this file. In the source project
([sgmuff/catholic-ai](https://github.com/sgmuff/catholic-ai)), the rest is
synced from the authored `frameworks/` directory by
`eval/sync_skill_bundle.py`; a test fails that project's CI if the bundle
ever drifts from what that script would produce. If you're working in that
project and just changed `frameworks/`, re-run the sync before testing
this skill — the bundle above, not the source directory, is what actually
gets read here.

## 1. Intake the incident and identify applicable frameworks

Ask what happened, in concrete terms: what the AI system did, what a
human relying on it did as a result, which system(s) and data or output
types were involved, roughly how many individuals are affected, and when
it was discovered (not when it happened, if the two differ — deadlines
below run from discovery, and the EU AI Act's own clock more precisely
from when a causal link, or the reasonable likelihood of one, is
established). Read
`${CLAUDE_SKILL_DIR}/references/frameworks/index.md` in full. For each
entry, ask or infer whether it applies (a high-risk AI system under the
EU AI Act's Annex III categories, in scope of the Act's territorial reach
→ EU AI Act serious-incident reporting; an institution that has adopted
the NIST AI RMF to structure its own incident response → NIST AI RMF).
Read the specific file(s) that apply in full — the EU AI Act's
`required_elements` states its own reporting deadlines and the exact
definition of a "serious incident." Record every framework considered in
`frameworks_considered`, including ones ruled inapplicable, so the record
shows the reasoning happened rather than being skipped.

## 2. Score severity

Assess severity — `low`, `moderate`, `high`, or `critical` — from the
specific facts: whether the incident meets the EU AI Act's "serious
incident" definition (death or serious harm to health, a serious and
irreversible disruption of critical infrastructure, an infringement of a
fundamental-rights obligation, or serious harm to property or the
environment), the scale of individuals affected, and whether harm has
actually materialized versus remaining a possibility. Write a rationale
grounded in those facts, not a restatement of what the level name means.

## 3. Identify every notification obligation, then gaps and escalation

For each framework marked `applicable`, check whether it imposes its own
notification or reporting duty. Under the EU AI Act, a serious incident
involving a high-risk AI system must be reported to the market
surveillance authority — the deadline depends on the incident's own
tier: 15 days generally, 2 days for a widespread infringement or a
critical-infrastructure disruption, 10 days for one involving a person's
death (Art. 73(2)-(4)). Calculate each `due_date` from
`incident.discovered_date` and write the arithmetic, including which tier
applies and why, into that obligation's `basis`. A voluntary framework
like the NIST AI RMF has no statutory deadline of its own — if the
institution has adopted an internal target under its own profile, record
that target here with its own stated basis rather than inventing a
regulatory one. List every obligation that applies — do not collapse
multiple audiences into one; they're independent duties that can all be
live at once.

Note anything still needed before every obligation can be discharged —
most often confirming the causal link between the AI system and the harm
(the EU AI Act's own reporting trigger), but also containment status or
scope confirmation. Mark each gap `blocking: true` only if it genuinely
blocks meeting a notification deadline. Then determine `escalation`: does
this incident meet a predefined severity, safety, legal, or
executive-reporting threshold? State the specific threshold met, or
plainly say why none was.

## 4. Write and render the record

Write a JSON file matching
`${CLAUDE_SKILL_DIR}/references/incident-schema.md` exactly, then run:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/incident.py --input <path-to-json> --out-dir <reports-dir>
```

`<reports-dir>` is `reports/` created next to wherever you're working in
this conversation, unless the user asks for somewhere else.

The script validates before it renders: every framework id real, every
notification obligation's framework marked applicable, every `due_date`
not before `discovered_date`, every gap has a description and a boolean
`blocking` flag, `severity.level` one of the four defined levels, and —
enforcing this project's own hard rule on Catholic language — the
`compliance` field rejected if any Catholic Social Teaching vocabulary has
leaked into it. A non-zero exit with "Could not build incident record" on
stderr lists every problem found; fix the JSON and rerun rather than
working around the validation. A zero exit may still print non-fatal
warnings on stderr about a field running long — reread the flagged parts
for restated or padded text before treating the report as final.

## 5. Report back in plain language, briefly

This is an advisory draft, grounded in a working interpretation of the
frameworks actually applied above — not a legal opinion — and it requires
AI-governance-lead or legal review before any notification is sent. State
severity and every notification deadline plainly and up front — the
earliest one first — then whether escalation applies and what's still
blocking. This is a summary, not a restatement of the full report. Close
by pointing the user to the rendered report file for the full basis.

## Human oversight and escalation

This skill never sends the actual notification to a regulator or any
other party, never makes a final determination that an incident doesn't
require reporting, and never approves delaying a report on anyone's
behalf — it drafts a finding for a named accountable person to review and
act on. Escalate plainly, rather than only noting in the report, anything
the `escalation` field marks `required`, any deadline that's already
close or passed, and any severity assessed `high` or `critical`
regardless of what `escalation.required` says.

## Grounding

Personalism and the dignity of the human person ground why those affected
by an AI system's failure are owed a prompt, honest accounting of what
happened, not a risk to be managed quietly. The primacy of human judgment
over automated determination grounds why an AI incident gets the same
seriousness as a human failure would, not a lesser one because a system
was involved. Subsidiarity keeps the response as close as possible to
those actually affected. Solidarity weighs toward disclosure when
severity is genuinely uncertain rather than treating uncertainty as
grounds to delay. This reasoning belongs in `cst_reflection`, alongside
the compliance findings, never inside them.
