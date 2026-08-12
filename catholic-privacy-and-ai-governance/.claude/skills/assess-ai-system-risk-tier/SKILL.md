---
name: assess-ai-system-risk-tier
description: >
  Classifies a described AI system against the EU AI Act's risk tiers
  (prohibited, high-risk, limited-risk, or minimal-risk) and maps it to
  NIST AI RMF's Govern/Map/Measure/Manage functions, then scores it against
  a seven-dimension AI-governance rubric — risk classification, governance
  and accountability, data governance, transparency and documentation,
  accuracy/robustness/security, bias and fairness, and human oversight.
  Flags which obligations attach given the system's tier. Produces a report
  that requires an AI governance lead or legal review before being relied
  on. Use when someone is building, deploying, or procuring a new AI system
  or feature and wants its risk tier and governance posture assessed, or
  asks for an AI risk classification by name.
---

# Classify an AI system's risk tier and governance posture

Produces one advisory finding for one AI system: not a certification, not a
legal opinion, and not a substitute for the AI governance lead or legal
review it explicitly requires before the system is deployed or its use
continues.

The judgment happens here, in conversation, grounded in this skill's own
bundled `references/rubric/ai-criteria.md` and `references/frameworks/`. No
API call, no separate rater. `scripts/assessment.py` only validates the
finished judgment against the real rubric dimensions and framework ids, and
renders it; it never scores anything itself. Read the actual rubric and
framework content before scoring anything — don't score from memory of what
a dimension, a risk tier, or a framework "usually" means.

**This skill is rubric-only, deliberately**, the same as its privacy-domain
sibling. There is no bright-line gate that short-circuits scoring for a
fixed list of disqualifying uses — though note step 3 below: an EU AI Act
*prohibited practice* is a bright line in the law itself, and gets stated
as a compliance finding regardless of how the rubric scores.

Every path below is written as `${CLAUDE_SKILL_DIR}/...`, a substitution
Claude Code resolves to this skill's own directory regardless of whether
it's installed inside a full checkout of the source project, as a plugin,
or standalone. If that substitution doesn't happen in your current
environment, resolve the same path relative to the folder containing this
`SKILL.md` instead.

## Architecture

Everything this skill reads or runs at assessment time lives inside its own
directory:

- `references/rubric/ai-criteria.md` — the seven-dimension AI-governance
  rubric scored in step 3: how to score each dimension, the passing
  threshold, and what a mitigation/`ideal`/`contested` flag each require.
- `references/frameworks/index.md` — the current framework registry,
  filtered to `domain: ai-governance`, read in step 2 to decide which laws
  or standards apply. Never hard-code a framework name anywhere in this
  procedure; read this file fresh every time, because the registry can
  grow or shrink independently of this `SKILL.md`.
- `references/frameworks/*/*.yaml` — the full content of every active
  framework: its trigger, required elements, and exact terms of art. Read
  the specific file(s) that apply in full before scoring.
- `references/assessment-schema.md` — the exact JSON shape step 4 writes.
- `scripts/assessment.py`, plus its sibling modules `rubric.py`,
  `language.py`, `concision.py`, `report.py` — the validate-and-render CLI
  step 4 calls. Dependency-free, stdlib-only Python, identical to its
  privacy-domain sibling's copies (this skill's own `assessment.py`
  discovers its rubric file by name rather than hardcoding one, so the
  same script works whichever skill it's bundled into).

This bundle is generated, not hand-edited, except for
`scripts/assessment.py` itself and this file. In the source project
([sgmuff/catholic-ai](https://github.com/sgmuff/catholic-ai)), the rest is
synced from the authored `frameworks/` and `rubric/` directories by
`eval/sync_skill_bundle.py`, driven by this skill's own entry in
`family-manifest.yaml`; a test fails that project's CI if the bundle ever
drifts from what that script would produce.

## 1. Intake the AI system

Ask what the system is, what it does, what decision or output it produces,
who builds or operates it, what data it uses (training, input, or both),
who receives or acts on its output, and how long its inputs, outputs, or
logs are kept. Stop asking once there's enough to reason about every rubric
dimension — not a fixed questionnaire run to exhaustion.

When part of this — a vendor's or model provider's public model card or
documentation — plausibly has a public source, offer the user a choice:
supply it directly, or have this skill search for it and bring back what it
finds, cited with a link, for the user to confirm before it's relied on
(build-plan.md §2.4). This never extends to searching for information about
the specific people the system acts on.

## 2. Identify applicable frameworks and determine the risk tier

Read `${CLAUDE_SKILL_DIR}/references/frameworks/index.md` in full. For the
EU AI Act specifically: check the system against Art. 5's prohibited
practices first, then Annex III's high-risk categories, then Art. 50's
transparency-only triggers, in that order — a system can only fall into
one tier, and the tier determines which of Chapter III's obligations
(Articles 9-15) actually attach. For NIST AI RMF, ask whether the user
wants to be assessed against it (it's voluntary). Read the specific
file(s) that apply in full before scoring. Record every framework
considered in `frameworks_considered` — including ones ruled inapplicable
— and state the risk-tier determination and its basis there, in the
framework's own terms (see `references/assessment-schema.md`).

## 3. Score the rubric

Read `${CLAUDE_SKILL_DIR}/references/rubric/ai-criteria.md` in full — all
seven dimensions and the shared scoring instructions at the top. For each
dimension:

- Score 1-5 against that dimension's own 5/3/1 anchors, calibrated to what's
  proportionate for the system's actual risk tier — a minimal-risk system
  doesn't need high-risk-grade documentation to score well.
- Write a real rationale: the specific fact that drove the score, one to
  three sentences, never a restatement of the dimension's own description.
- If the score is below the rubric's stated passing threshold, write a
  concrete mitigation — a specific change to the system or its governance,
  not "be more careful" and not a request for information intake should
  already have gathered.
- Write an `ideal` regardless of score.
- Mark `contested: true` only when two dimensions genuinely pull against
  each other for this system (e.g. a transparency obligation against a
  legitimate trade-secret or security concern about model internals) — a
  signal for human judgment, not something to average away.

If step 2 found the system matches an EU AI Act prohibited practice, say so
plainly before scoring and note in `compliance` that no mitigation can cure
a prohibited use — the system may not be placed on the market or used as
described, full stop. Still score the rubric dimensions if useful context
for redesigning the system, but don't let a mitigation on any dimension
imply the prohibition itself has a workaround.

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
Catholic Social Teaching vocabulary has leaked into it. A non-zero exit
with "Could not build assessment" on stderr lists every problem found; fix
the JSON and rerun rather than working around the validation. A zero exit
may still print non-fatal warnings on stderr about a field or section
running long — reread the flagged parts for restated or padded text before
treating the report as final.

## 5. Report back in plain language, briefly

This is an advisory draft, grounded in a working interpretation of the
frameworks actually applied above — not a legal opinion — and it requires
an AI governance lead or legal review before the system is deployed or its
use continues. State the risk tier, the verdict, and what's weakest; this
is a summary, not a restatement of the full report. Flag a prohibited-
practice match, or any high-risk system missing a required Chapter III
obligation entirely, as needing escalation before proceeding, not just
noted in the report. Close by pointing the user to the rendered report file
for the full rationale on every dimension.

## Human oversight and escalation

This skill never sends a legally significant communication, never makes a
final risk-classification or compliance determination, and never approves
an exception on anyone's behalf — it drafts a finding for a named
accountable person to review. Escalate plainly, rather than only noting in
the report, anything involving a prohibited-practice match, a missing
required safeguard for a high-risk system, or a decision that needs
executive or legal authority. Document the rationale behind the finding;
the disposition — whether the system proceeds, is modified, or is stopped —
stays a human decision every time.

## Grounding

Personalism and the dignity of the human person (Catechism §§356-357, 1700)
ground why this matters beyond the law: a system that decides, recommends,
or acts on someone's behalf is answerable to that person, not just to a
regulator. Subsidiarity (Compendium of the Social Doctrine of the Church
§§185-187) keeps accountability for the system's behavior close to someone
who can actually act on a finding, not diffused across an organization no
one person is answerable for. Solidarity (Compendium §§192-194; John Paul
II, *Sollicitudo Rei Socialis* §38) asks whether the system was checked for
a disparate impact on people it's likely to affect differently, not just
for the harm it obviously avoids. The primacy of human judgment over
automated determination (*Antiqua et Nova*, DDF & Dicastery for Culture and
Education, 28 Jan. 2025, §44: "ultimate responsibility for decisions made
using AI rests with the human decision-makers") grounds the human-oversight
dimension specifically — the same claim the privacy-domain rubric's own
human-oversight dimension rests on, applied here to an AI system's own
operation rather than to a downstream automated decision about personal
data. Full citations: build-plan.md §2.3. This reasoning belongs in
`cst_reflection`, alongside the compliance findings, never inside them.

`render_markdown` puts this section first, as the report's Catholic Social
Teaching summary (build-plan.md §2.1 amendment) — so write it to name what
the rubric actually found for this system, not just the grounding in the
abstract: which dimensions scored where, and why that matters in this
theological register. A reader who stops after this section should still
walk away knowing something true and specific about this assessment, not
just the general principles behind it.
