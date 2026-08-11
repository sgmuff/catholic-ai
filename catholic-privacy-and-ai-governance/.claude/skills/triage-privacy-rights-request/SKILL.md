---
name: triage-privacy-rights-request
description: >
  Triages an incoming data-subject rights request — access, deletion,
  correction, portability, restriction, or objection — against the current
  framework registry (GDPR Chapter III, CCPA/CPRA, HIPAA, FERPA, plus
  whatever else is registered). Identifies which frameworks apply,
  calculates the governing response deadline from the request's received
  date, and flags outstanding gaps (most often identity verification)
  before a response is sent. Produces a report that requires DPO or legal
  review before any response goes out. Use when an access, deletion,
  correction, portability, restriction, or objection request has come in
  from a data subject and the response deadline and requirements need
  working out. Not for a data breach or security incident — use
  `triage-privacy-incident` for that instead.
---

# Triage a data-subject rights request

Produces one advisory finding for one incoming request: not a legal
opinion, and not a substitute for the DPO or legal review it explicitly
requires before any response is sent.

This is a different task shape from this family's assessment skills
(`draft-privacy-impact-assessment`, `draft-privacy-notice-update`): a
rights request isn't scored across ongoing-quality dimensions, it's
classified, given a deadline, and checked for what's still missing. The
judgment happens here, in conversation, grounded in this skill's own
bundled `references/frameworks/`. No API call, no separate rater.
`scripts/triage.py` only validates the finished judgment against the real
framework ids and internal date logic, and renders it; it never classifies
or calculates anything itself. Read the actual framework content before
determining applicability or a deadline — don't reason from memory of what
a framework "usually" requires.

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
  framework: its trigger, required elements (including the exact response
  deadline provision), and terms of art. Read the specific file(s) that
  apply in full before determining applicability or calculating a
  deadline — never work from memory of what a framework "usually"
  requires.
- `references/triage-schema.md` — the exact JSON shape step 3 writes.
- `scripts/triage.py`, plus its sibling modules `language.py`,
  `concision.py`, `report.py` — the validate-and-render CLI step 3 calls.
  Dependency-free, stdlib-only Python (no `pyyaml`, no install step), so it
  runs with a plain `python3` wherever this skill ends up. Validates the
  written triage record against the real framework ids in `references/`,
  checks the calculated deadline against the received date, enforces the
  compliance/CST language boundary, flags anything unusually long, and
  renders the Markdown report. Unlike its sibling skills, this bundle has
  no `rubric.py` and no `references/rubric/` — there's no rubric here to
  parse.

This bundle is generated, not hand-edited, except for `scripts/triage.py`
itself and this file. In the source project
([sgmuff/catholic-ai](https://github.com/sgmuff/catholic-ai)), the rest is
synced from the authored `frameworks/` directory by
`eval/sync_skill_bundle.py`; a test fails that project's CI if the bundle
ever drifts from what that script would produce. If you're working in that
project and just changed `frameworks/`, re-run the sync before testing
this skill — the bundle above, not the source directory, is what actually
gets read here.

## 1. Intake the request and identify applicable frameworks

Ask what the requester asked for (in their own words), which right it maps
to (access, deletion, correction, portability, restriction, objection),
how and when it arrived, and who's asking and their relationship to the
data. Read `${CLAUDE_SKILL_DIR}/references/frameworks/index.md` in full.
For each entry, ask or infer whether the triggering jurisdiction or facts
apply (a diocese handling an EU parishioner's request → GDPR; a US
Catholic hospital and a request for medical records → HIPAA; a business
serving a California resident → CCPA/CPRA). Read the specific file(s) that
apply in full — every applicable framework's `required_elements` states
its own response-deadline provision and citation. Record every framework
considered in `frameworks_considered`, including ones ruled inapplicable,
so the record shows the reasoning happened rather than being skipped.

## 2. Calculate the governing deadline

Among every framework marked `applicable`, the shortest applicable
deadline governs the response. Calculate `response_due` from
`request.received_date` using that framework's own stated period (e.g.
GDPR Art. 12(3): one month from receipt; CCPA Civ. Code § 1798.130(a)(2):
45 calendar days; HIPAA 45 CFR 164.524(b)(2): 30 days). Write the
arithmetic into `governing_deadline.basis`, not just the resulting date.
If more than one framework applies with different periods, name the one
actually governing and say why it's the tightest constraint — don't
average or split the difference.

## 3. Identify gaps, then write and render the record

Note anything still needed before the request can be answered — most
often identity verification, but also scope clarification (does "all data"
really mean every system, or the one the requester named?) or an
exemption determination a framework's `required_elements` allows. Mark
each gap `blocking: true` only if it genuinely pauses the response clock
under the governing framework, not merely because it's inconvenient.

Write a JSON file matching
`${CLAUDE_SKILL_DIR}/references/triage-schema.md` exactly, then run:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/triage.py --input <path-to-json> --out-dir <reports-dir>
```

`<reports-dir>` is `reports/` created next to wherever you're working in
this conversation, unless the user asks for somewhere else.

The script validates before it renders: every framework id real, the
governing deadline's framework marked applicable, `response_due` not
before `received_date`, every gap has a description and a boolean
`blocking` flag, and — enforcing this project's own hard rule on Catholic
language — the `compliance` field rejected if any Catholic Social Teaching
vocabulary has leaked into it. A non-zero exit with "Could not build
triage record" on stderr lists every problem found; fix the JSON and
rerun rather than working around the validation. A zero exit may still
print non-fatal warnings on stderr about a field running long — reread the
flagged parts for restated or padded text before treating the report as
final.

## 4. Report back in plain language, briefly

This is an advisory draft, grounded in a working interpretation of the
frameworks actually applied above — not a legal opinion — and it requires
DPO or legal review before any response is sent. State the governing
deadline plainly and up front, then what's still blocking. This is a
summary, not a restatement of the full report. Close by pointing the user
to the rendered report file for the full basis.

## Human oversight and escalation

This skill never sends the actual response to the requester, never makes
a final determination that a request is exempt or excessive, and never
approves an extension on anyone's behalf — it drafts a finding for a named
accountable person to review and act on. Escalate plainly, rather than
only noting in the report, anything involving a legal interpretation of an
exemption, a request that looks manifestly unfounded or excessive, or a
deadline that's already close or passed.

## Grounding

Personalism and the dignity of the human person ground a data subject's
claim to their own data — a request is owed a response, not granted as a
favor. Subsidiarity keeps the decision about the data as close as possible
to the person concerned. Solidarity weighs toward the requester when a
request is ambiguous rather than treating ambiguity as grounds to delay.
This reasoning belongs in `cst_reflection`, alongside the compliance
findings, never inside them.
