---
name: triage-privacy-incident
description: >
  Triages a reported privacy incident or possible data breach against the
  current framework registry (GDPR breach notification, California's
  breach notification law, HIPAA's Breach Notification Rule, plus whatever
  else is registered). Identifies which frameworks apply, scores the
  incident's severity, identifies every independent notification
  obligation this incident triggers — to a supervisory authority, affected
  individuals, or others, each with its own deadline — flags outstanding
  gaps, and states plainly whether it meets the threshold for escalation.
  Produces a report that requires DPO or legal review before any
  notification is sent. Use when a possible data breach, unauthorized
  disclosure, or other privacy incident has been reported and its
  severity, notification obligations, and escalation need working out.
  Not for an access, deletion, correction, portability, restriction, or
  objection request from a data subject — use
  `triage-privacy-rights-request` for that instead.
---

# Triage a privacy incident

Produces one advisory finding for one reported incident: not a legal
opinion, and not a substitute for the DPO or legal review it explicitly
requires before any notification is sent or the incident is closed.

This is a close sibling of `triage-privacy-rights-request` — both classify
a point-in-time event and calculate a deadline rather than scoring an
ongoing activity across quality dimensions — but not the same shape. A
rights request has one requester and one governing deadline; an incident
can trigger several **independent, simultaneous** notification
obligations to different audiences at once (a supervisory authority under
one framework, affected individuals under another, a state attorney
general under a third) — none of which "governs" over the others the way
a single response deadline does. `notification_obligations` below is a
list for exactly that reason, not a single `governing_deadline` field.

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
  in step 1 to decide which laws apply. Never hard-code a framework name
  anywhere in this procedure; read this file fresh every time, because the
  registry can grow or shrink independently of this `SKILL.md`.
- `references/frameworks/*/*.yaml` — the full content of every active
  framework: its trigger, required elements (including each notification
  provision's exact deadline and audience), and terms of art. Read the
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
  `triage-privacy-rights-request`, this bundle has no `rubric.py` and no
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

Ask what happened, in concrete terms: what was disclosed, lost, or
accessed; which systems and data types were involved; roughly how many
individuals are affected; and when it was discovered (not when it
happened, if the two differ — deadlines below run from discovery). What
actually happened is internal information only the user has, and this
skill never searches for or about the individuals affected — but if a
vendor is involved and has already published its own advisory or
notification about this same incident, offer to find and cite it as
corroborating context, confirmed by the user (build-plan.md §2.4). Read
`${CLAUDE_SKILL_DIR}/references/frameworks/index.md` in full. For each
entry, ask or infer whether the triggering jurisdiction or facts apply (a
diocese with EU parishioners in the affected data → GDPR breach
notification; California residents affected → California's breach
notification law; a US Catholic hospital and PHI → HIPAA's Breach
Notification Rule). Read the specific file(s) that apply in full — every
applicable framework's `required_elements` states its own notification
deadline, audience, and citation. Record every framework considered in
`frameworks_considered`, including ones ruled inapplicable, so the record
shows the reasoning happened rather than being skipped.

## 2. Score severity

Assess severity — `low`, `moderate`, `high`, or `critical` — from the
specific facts: the sensitivity of the data involved, the scale of
individuals affected, whether the exposure stayed internal or reached an
external or malicious party, and whether there's evidence of actual
misuse versus mere possibility of access. Write a rationale grounded in
those facts, not a restatement of what the level name means.

## 3. Identify every notification obligation, then gaps and escalation

For each framework marked `applicable`, check whether it imposes its own
notification duty — not every applicable framework does (some govern
consent or retention, not breach response). For each one that does,
calculate its `due_date` from `incident.discovered_date` using that
framework's own stated period (e.g. GDPR Art. 33(1): 72 hours to the
supervisory authority; California Civ. Code § 1798.82(a)(2)(A): 30
calendar days to affected residents; HIPAA 45 CFR 164.400-414: 60 days to
affected individuals and HHS). Write the arithmetic into each
obligation's `basis`, not just the resulting date. List every obligation
that applies — do not collapse multiple audiences into one, and do not
pick a single "governing" one the way `triage-privacy-rights-request`
does; they're independent duties that can all be live at once.

Note anything still needed before every obligation can be discharged —
most often confirming the full scope of affected individuals, but also
containment status or a pending legal determination. Mark each gap
`blocking: true` only if it genuinely blocks meeting a notification
deadline. Then determine `escalation`: does this incident meet a
predefined severity, notification, legal, or executive-reporting
threshold? State the specific threshold met, or plainly say why none was.

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
DPO or legal review before any notification is sent. State severity and
every notification deadline plainly and up front — the earliest one
first — then whether escalation applies and what's still blocking. This
is a summary, not a restatement of the full report. Close by pointing the
user to the rendered report file for the full basis.

## Human oversight and escalation

This skill never sends the actual notification to a regulator, individual,
or any other party, never makes a final determination that an incident
doesn't require notification, and never approves delaying a notification
on anyone's behalf — it drafts a finding for a named accountable person to
review and act on. Escalate plainly, rather than only noting in the
report, anything the `escalation` field marks `required`, any deadline
that's already close or passed, and any severity assessed `high` or
`critical` regardless of what `escalation.required` says.

## Grounding

Personalism and the dignity of the human person (Catechism §§356-357, 1700)
ground why those affected are owed a prompt, honest accounting of what
happened to their data, not a risk to be managed quietly. Subsidiarity
(Compendium of the Social Doctrine of the Church §§185-187) keeps the
response as close as possible to those actually affected rather than
deferring entirely to process. Solidarity (Compendium §§192-194; John Paul
II, *Sollicitudo Rei Socialis* §38) weighs toward disclosure when severity
is genuinely uncertain rather than treating uncertainty as grounds to
delay. Full citations: build-plan.md §2.3. This reasoning belongs in
`cst_reflection`, alongside the compliance findings, never inside them.
