---
name: draft-model-card
description: >
  Produces a model or system documentation record (a model card) for an AI
  system, by first scoring the system against the current framework
  registry and the same seven-dimension AI-governance rubric
  assess-ai-system-risk-tier uses, then drafting card content grounded in
  what the assessment found — including its limitations, not only its
  intended purpose. Produces both a validated assessment report and a
  proposed model card that require AI-governance-lead or legal review
  before the card is published or attached to the system's own
  documentation. Use when an AI system or model needs a documentation
  record, or asks for a model card by name.
---

# Draft a model or system documentation record

Produces two things from one assessment: a validated finding — identical
in rigor to `assess-ai-system-risk-tier`'s own — and a proposed model card
grounded in that finding. Not a certification, not a legal opinion, and
not a substitute for the AI-governance-lead or legal review both
explicitly require before anything gets published.

This skill scores the exact same rubric its sibling does, for a reason
worth stating plainly: a model card that describes a system as designed,
rather than as it actually performs, isn't documentation — it's marketing
copy wearing documentation's shape. The assessment comes first,
unconditionally, because what the card is allowed to claim about accuracy,
robustness, bias, and human oversight is bounded by what the assessment
actually found, not by what would read most reassuringly.

Every path below is written as `${CLAUDE_SKILL_DIR}/...`, a substitution
Claude Code resolves to this skill's own directory regardless of whether
it's installed inside a full checkout of the source project, as a plugin,
or standalone. If that substitution doesn't happen in your current
environment, resolve the same path relative to the folder containing this
`SKILL.md` instead.

## Architecture

This skill's `references/` and `scripts/` are the same bundle
`assess-ai-system-risk-tier` carries — same rubric
(`references/rubric/ai-criteria.md`), same AI-governance framework
registry (`references/frameworks/`, now including `iso-42001` — Annex A.8
"Information for interested parties" is this skill's most direct
grounding), same dependency-free validate-and-render CLI. Nothing here is
a fork of that logic; both skills are synced from this project's single
authored `rubric/ai-criteria.md` and `frameworks/ai-governance/`, so a
change to either is reflected in both the next time the source project
re-runs its sync — there is no second copy of the rubric to drift out of
step with the first.

What's specific to this skill is step 5 below: drafting the actual model
card content. That happens directly in this conversation, grounded in the
validated assessment, and is never written into or validated by
`scripts/assessment.py` — a model card is a document to be read and
approved by a person, not a structured record with a schema to enforce.

## 1. Intake the system

Ask what the system does, what it's for and who it serves, what data it
uses (training, input, or both), what systems it runs in, who acts on its
output, and how long inputs/outputs/training-derived data are kept. Stop
asking once there's enough to reason about every rubric dimension, the
same discipline `assess-ai-system-risk-tier` follows.

When part of this — the underlying model's own public model card, technical
report, or provider documentation — plausibly has a public source, offer
the user a choice: supply it directly, or have this skill search for it and
bring back what it finds, cited with a link, for the user to confirm before
it's relied on (build-plan.md §2.4). This never extends to searching for
information about the specific people the system acts on.

## 2. Identify applicable frameworks

Read `${CLAUDE_SKILL_DIR}/references/frameworks/index.md` in full, exactly
as `assess-ai-system-risk-tier` step 2 does — the same registry, filtered
the same way, never hard-coded here.

## 3. Score the rubric

Read `${CLAUDE_SKILL_DIR}/references/rubric/ai-criteria.md` in full and
score the system against all seven dimensions, exactly as
`assess-ai-system-risk-tier` step 3 does. This is not optional or
abbreviated because the deliverable is a card rather than a full risk-tier
assessment — the card's honesty depends on this assessment being done with
the same rigor.

## 4. Write the assessment and render the report

Write a JSON file matching
`${CLAUDE_SKILL_DIR}/references/assessment-schema.md`, then run:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/assessment.py --input <path-to-json> --out-dir <reports-dir>
```

Same validation, same §2.1/§2.2 enforcement, same non-zero-exit-lists-every-
problem behavior as `assess-ai-system-risk-tier` step 4.

## 5. Draft the model card

Only after the assessment validates: draft the card content, directly in
this conversation, not as part of the JSON or the rendered report. Ground
every claim in what step 3 actually found — cover intended purpose,
inputs and outputs, training data provenance and known limitations,
performance characteristics, and the human-oversight mechanism the
assessment identified, stated as it actually exists, not as it would
ideally exist. If a dimension scored below the rubric's passing threshold,
the card either discloses the gap honestly or waits until the mitigation
is actually in place; it never states the *ideal* as though it were the
current system. Offer the draft as text in the conversation, and, if the
user wants it saved, write it to a plain file next to the rendered
assessment report rather than through `scripts/assessment.py` — a card
draft is prose to be edited, not a structured record to be validated.

## 6. Report back in plain language, briefly

State the verdict on the system and what the card needed to include to
reflect it honestly — a summary, not a restatement of the full assessment
or the full card draft. Flag anything that met a high-risk threshold as
needing escalation before the card is published, not just noted in the
report. Close by pointing the user to both the rendered assessment report
and the card draft.

## Human oversight and escalation

Same standing rule as every skill in this family: never sends a legally
significant communication, never makes a final compliance determination,
and never approves a model card for publication on anyone's behalf — it
drafts a finding and draft content for a named accountable person to
review. Escalate plainly, rather than only noting in the report, anything
the assessment found that an existing card for this system already
misrepresents, since documentation that's actively wrong is a more urgent
problem than documentation that's merely incomplete.

## Grounding

Same grounding as `assess-ai-system-risk-tier`'s own §7.3-equivalent —
personalism, subsidiarity, solidarity, and the primacy of human judgment
over automated determination, each with its own citation at build-plan.md
§2.3 — with one dimension specific to this skill's own purpose: a model
card is how a system that acts on a person remains answerable to the
people who rely on it or are affected by it.
Documentation that's technically accurate but written to obscure a real
limitation isn't honoring that; it's exploiting the gap between disclosure
and comprehension. This reasoning belongs in `cst_reflection`, alongside
the compliance findings, never inside them — and never inside the card
draft itself, which stays in plain, direct language a reader without any
theology can act on.

`render_markdown` puts this section first, as the report's Catholic Social
Teaching summary (build-plan.md §2.1 amendment) — so write it to name what
the rubric actually found for this system, not just the grounding in the
abstract. A reader who stops after this section should still walk away
knowing something true and specific about this assessment.
