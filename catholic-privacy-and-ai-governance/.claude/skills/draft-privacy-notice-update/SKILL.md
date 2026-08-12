---
name: draft-privacy-notice-update
description: >
  Drafts a proposed revision to a privacy notice or policy section for a
  stated change in practice — a new system, a new data element, a new
  recipient, or a new retention period — by first scoring the changed
  practice against the current framework registry and the same
  seven-dimension privacy-by-design rubric
  draft-privacy-impact-assessment uses, then drafting notice language that
  honestly discloses what the assessment found, not just what the practice
  was designed to do. Produces both a validated assessment report and
  proposed notice text that require DPO or legal review before the notice
  is published. Use when someone needs to update a privacy notice, privacy
  policy, or a section of one because a data-processing practice has
  changed, or asks for a privacy notice update by name.
---

# Draft a privacy notice or policy revision for a changed practice

Produces two things from one assessment: a validated finding — identical in
rigor to `draft-privacy-impact-assessment`'s own — and proposed notice
language grounded in that finding. Not a certification, not a legal
opinion, and not a substitute for the DPO or legal review both explicitly
require before anything gets published.

This skill scores the exact same rubric its sibling does, for a reason
worth stating plainly: a notice that describes a practice as designed,
rather than as it actually operates, isn't a notice — it's marketing copy
wearing a notice's shape. The assessment comes first, unconditionally,
because what the notice is allowed to claim is bounded by what the
assessment actually found, not by what would read most reassuringly.

Every path below is written as `${CLAUDE_SKILL_DIR}/...`, a substitution
Claude Code resolves to this skill's own directory regardless of whether
it's installed inside a full checkout of the source project, as a plugin,
or standalone. If that substitution doesn't happen in your current
environment, resolve the same path relative to the folder containing this
`SKILL.md` instead.

## Architecture

This skill's `references/` and `scripts/` are the same bundle
`draft-privacy-impact-assessment` carries — same rubric
(`references/rubric/criteria.md`), same privacy framework registry
(`references/frameworks/`), same dependency-free validate-and-render CLI.
Nothing here is a fork of that logic; both skills are synced from this
project's single authored `rubric/criteria.md` and `frameworks/privacy/`,
so a change to either is reflected in both the next time the source project
re-runs its sync — there is no second copy of the rubric to drift out of
step with the first.

What's specific to this skill is step 5 below: drafting the actual notice
language. That happens directly in this conversation, grounded in the
validated assessment, and is never written into or validated by
`scripts/assessment.py` — a notice is a piece of writing to be read and
approved by a person, not a structured record with a schema to enforce.

## 1. Intake the changed practice

Ask what's changing: the new or modified system, the data elements
involved, who now receives the data, how long it's kept, and — critically
for a notice update specifically — what the *current* notice or policy
already says about this practice, if anything. Stop asking once there's
enough to reason about every rubric dimension, the same discipline
`draft-privacy-impact-assessment` follows.

The *current* published notice or policy text is itself a natural candidate
for this: offer the user a choice — paste the current language directly, or
have this skill search for and fetch the published page, cited with a link,
for the user to confirm before it's treated as the baseline (build-plan.md
§2.4). This never extends to searching for information about the specific
people the practice concerns.

## 2. Identify applicable frameworks

Read `${CLAUDE_SKILL_DIR}/references/frameworks/index.md` in full, exactly
as `draft-privacy-impact-assessment` step 2 does — the same registry,
filtered the same way, never hard-coded here.

## 3. Score the rubric

Read `${CLAUDE_SKILL_DIR}/references/rubric/criteria.md` in full and score
the changed practice against all seven dimensions, exactly as
`draft-privacy-impact-assessment` step 3 does. This is not optional or
abbreviated because the deliverable is a notice rather than a full DPIA —
the notice's honesty depends on this assessment being done with the same
rigor.

## 4. Write the assessment and render the report

Write a JSON file matching
`${CLAUDE_SKILL_DIR}/references/assessment-schema.md`, then run:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/assessment.py --input <path-to-json> --out-dir <reports-dir>
```

Same validation, same §2.1/§2.2 enforcement, same non-zero-exit-lists-every-
problem behavior as `draft-privacy-impact-assessment` step 4.

## 5. Draft the notice language

Only after the assessment validates: draft the specific notice or policy
section text, directly in this conversation, not as part of the JSON or
the rendered report. Ground every claim in what step 3 actually found —
if a dimension scored below the rubric's passing threshold, the notice
either discloses the gap honestly or waits until the mitigation is actually
in place; it never states the *ideal* as though it were the current
practice. Keep the draft to the specific section that changed, not a
rewrite of the whole notice, unless the user asks for the whole document.
Offer the draft as text in the conversation, and, if the user wants it
saved, write it to a plain file next to the rendered assessment report
rather than through `scripts/assessment.py` — a notice draft is prose to be
edited, not a structured record to be validated.

## 6. Report back in plain language, briefly

State the verdict on the underlying practice and what the notice needed to
change to reflect it — a summary, not a restatement of the full assessment
or the full notice draft. Flag anything that met a high-risk threshold as
needing escalation before the notice is published, not just noted in the
report. Close by pointing the user to both the rendered assessment report
and the notice draft.

## Human oversight and escalation

Same standing rule as every skill in this family: never sends a legally
significant communication, never makes a final compliance determination,
and never approves a notice for publication on anyone's behalf — it drafts
a finding and draft language for a named accountable person to review.
Escalate plainly, rather than only noting in the report, anything the
assessment found that the current notice already misrepresents, since a
notice that's actively wrong is a more urgent problem than one that's
merely incomplete.

## Grounding

Same grounding as `draft-privacy-impact-assessment` §7.3 — personalism,
subsidiarity, solidarity, and the primacy of human judgment over automated
determination, each with its own citation at build-plan.md §2.3 — with one
dimension specific to this skill's own purpose:
transparency itself is a form of respect for the person the notice is
written for. A notice that's technically accurate but written to be
skimmed past isn't honoring that; it's exploiting the gap between
disclosure and comprehension. This reasoning belongs in `cst_reflection`,
alongside the compliance findings, never inside them — and never inside
the notice draft itself, which stays in plain, direct language a reader
without any theology can act on.

`render_markdown` puts this section first, as the report's Catholic Social
Teaching summary (build-plan.md §2.1 amendment) — so write it to name what
the rubric actually found for this changed practice, not just the
grounding in the abstract. A reader who stops after this section should
still walk away knowing something true and specific about this assessment.
