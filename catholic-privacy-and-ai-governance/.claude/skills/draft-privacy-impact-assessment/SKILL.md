---
name: draft-privacy-impact-assessment
description: >
  Drafts a structured Data Protection/Privacy Impact Assessment (DPIA/PIA)
  for a described data-processing activity, new project, product, vendor
  relationship, or AI/technology use. Identifies which frameworks apply from
  the current registry (GDPR Art. 35, CCPA/CPRA, HIPAA, FERPA, or a
  voluntary standard like ISO/IEC 27701, plus whatever else is registered),
  scores the activity against a privacy-by-design rubric — necessity and
  proportionality, data minimization, lawful basis and consent, retention,
  security controls, third-party sharing, and human oversight of automated
  decisions. Produces a report that requires DPO or legal review before
  being relied on. Use when someone is starting something that will collect
  or process personal data and wants the privacy risk assessed, or asks for
  a PIA/DPIA/privacy impact assessment by name.
---

# Draft a Data Protection/Privacy Impact Assessment

Produces one advisory finding for one processing activity: not a
certification, not a legal opinion, and not a substitute for the DPO or
legal review it explicitly requires before the activity proceeds.

The judgment happens here, in conversation, grounded in this skill's own
bundled `references/rubric/criteria.md` and `references/frameworks/`. No API
call, no separate rater. `scripts/assessment.py` only validates the
finished judgment against the real rubric dimensions and framework ids, and
renders it; it never scores anything itself. Read the actual rubric and
framework content before scoring anything — don't score from memory of what
a dimension or a framework "usually" means.

**This skill is rubric-only, deliberately.** There is no bright-line gate
that short-circuits scoring for a fixed list of disqualifying uses. Every
activity gets scored on its own facts, across all seven dimensions.

Every path below is written as `${CLAUDE_SKILL_DIR}/...`, a substitution
Claude Code resolves to this skill's own directory regardless of whether
it's installed inside a full checkout of the source project, as a plugin, or
standalone. If that substitution doesn't happen in your current environment,
resolve the same path relative to the folder containing this `SKILL.md`
instead.

## Architecture

Everything this skill reads or runs at assessment time lives inside its own
directory:

- `references/rubric/criteria.md` — the seven-dimension privacy-by-design
  rubric scored in step 3: how to score each dimension, the passing
  threshold, and what a mitigation/`ideal`/`contested` flag each require.
- `references/frameworks/index.md` — the current framework registry, read
  in step 2 to decide which laws or standards apply. Never hard-code a
  framework name anywhere in this procedure; read this file fresh every
  time, because the registry can grow or shrink independently of this
  `SKILL.md`.
- `references/frameworks/*/*.yaml` — the full content of every active
  framework: its trigger, required elements, and exact terms of art. Read
  the specific file(s) that apply in full before scoring — never score from
  memory of what a framework "usually" requires.
- `references/assessment-schema.md` — the exact JSON shape step 4 writes.
- `scripts/assessment.py`, plus its sibling modules `rubric.py`,
  `language.py`, `concision.py`, `report.py` — the validate-and-render CLI
  step 4 calls. Dependency-free, stdlib-only Python (no `pyyaml`, no install
  step), so it runs with a plain `python3` wherever this skill ends up.
  Validates the written assessment against the real dimension ids and
  framework ids in `references/`, enforces the compliance/CST language
  boundary, flags anything unusually long, and renders the Markdown report.

This bundle is generated, not hand-edited, except for
`scripts/assessment.py` itself and this file. In the source project
([sgmuff/catholic-ai](https://github.com/sgmuff/catholic-ai)), the rest is
synced from the authored `frameworks/` and `rubric/` directories by
`eval/sync_skill_bundle.py`; a test fails that project's CI if the bundle
ever drifts from what that script would produce. If you're working in that
project and just changed `frameworks/` or `rubric/`, re-run the sync before
testing this skill — the bundle above, not the source directories, is what
actually gets read here.

## 1. Intake the processing activity

Ask what's being built or changed: what personal data it collects or
touches, who it's about, the purpose, which systems are involved, who
receives the data (internal teams, vendors, other institutions), where it's
stored, and how long it's kept. Stop asking once there's enough to reason
about every rubric dimension — not a fixed questionnaire run to exhaustion.

## 2. Identify applicable frameworks

Read `${CLAUDE_SKILL_DIR}/references/frameworks/index.md` in full. For each
entry:

- If it's a **law**, ask or infer whether the triggering jurisdiction or
  facts apply (a diocese handling EU parishioner data → GDPR; a US Catholic
  hospital → HIPAA; a university housing or enrollment system → FERPA; a
  business serving California residents → CCPA/CPRA).
- If it's a **standard**, ask whether the user wants to be assessed against
  it.

Read the specific file(s) that apply in full before scoring. Record every
framework considered in `frameworks_considered` — including ones ruled
inapplicable, so the record shows the reasoning happened rather than being
skipped (see `references/assessment-schema.md`).

## 3. Score the rubric

Read `${CLAUDE_SKILL_DIR}/references/rubric/criteria.md` in full — all seven
dimensions and the shared scoring instructions at the top. For each
dimension:

- Score 1-5 against that dimension's own 5/3/1 anchors, grounded in what the
  activity actually does — not what a better version of it would do.
- Write a real rationale: the specific fact that drove the score, one to
  three sentences, never a restatement of the dimension's own description.
- If the score is below the rubric's stated passing threshold, write a
  concrete mitigation — a specific change to the activity itself, not
  "be more careful" and not a request for information intake should already
  have gathered.
- Write an `ideal` regardless of score: what this dimension looks like at
  its best for this specific activity.
- Mark `contested: true` only when two dimensions genuinely pull against
  each other for this activity (e.g. minimization vs. a retention period a
  fraud or safety control actually needs) — a signal for human judgment, not
  something to average away.

## 4. Write the assessment and render the report

Write a JSON file matching
`${CLAUDE_SKILL_DIR}/references/assessment-schema.md` exactly, then run:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/assessment.py --input <path-to-json> --out-dir <reports-dir>
```

`<reports-dir>` is `reports/` created next to wherever you're working in
this conversation, unless the user asks for somewhere else.

The script validates before it renders: every rubric dimension present
exactly once, every framework id real, no missing mitigation below
threshold, `subject.retention` non-empty, and — enforcing this project's own
hard rule on Catholic language — the `compliance` field rejected if any
Catholic Social Teaching vocabulary has leaked into it. A non-zero exit with
"Could not build assessment" on stderr lists every problem found; fix the
JSON and rerun rather than working around the validation. A zero exit may
still print non-fatal warnings on stderr about a field or section running
long — reread the flagged parts for restated or padded text before treating
the report as final.

## 5. Report back in plain language, briefly

This is an advisory draft, grounded in a working interpretation of the
frameworks actually applied above — not a legal opinion — and it requires
DPO or legal review before the underlying activity proceeds. State the
verdict and what's weakest; this is a summary, not a restatement of the full
report. Flag anything that met a high-risk threshold (special-category
data, children's data, large-scale profiling, an automated decision with a
legal or similarly significant effect) as needing escalation before
proceeding, not just noted in the report. Close by pointing the user to the
rendered report file for the full rationale on every dimension.

## Human oversight and escalation

This skill never sends a legally significant communication, never makes a
final compliance determination, and never approves an exception on anyone's
behalf — it drafts a finding for a named accountable person to review.
Escalate plainly, rather than only noting in the report, anything involving
a legal interpretation, a material or high-risk finding, or a decision that
needs executive or legal authority. Document the rationale behind the
finding; the disposition — whether the activity proceeds, is modified, or is
stopped — stays a human decision every time.

## Grounding

Personalism and the dignity of the human person ground informational
self-determination: a person's data is an extension of the person, not a
resource to optimize. Subsidiarity keeps data-handling decisions and consent
as close as possible to the person concerned. Solidarity protects those
least able to contest how their data is used. The primacy of human judgment
over automated determination grounds the human-oversight dimension
specifically. This reasoning belongs in `cst_reflection`, alongside the
compliance findings, never inside them.

`render_markdown` puts this section first, as the report's Catholic Social
Teaching summary (build-plan.md §2.1 amendment) — so write it to name what
the rubric actually found for this activity, not just the grounding in the
abstract: which dimensions scored where, and why that matters in this
theological register. A reader who stops after this section should still
walk away knowing something true and specific about this assessment, not
just the general principles behind it.
