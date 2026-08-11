---
name: map-ai-regulatory-change
description: >
  Given an AI-specific regulatory or standards development pasted in by
  the user (this skill doesn't monitor feeds itself), summarizes it and
  maps its impact against the current framework registry — which
  registered frameworks are actually affected and why — then recommends
  whether to register a new framework, update an existing required
  element, retire a framework, or take no action. Produces a report that
  requires an AI-governance-lead or legal review before any registry
  change is made. Use when a new AI-specific law, regulation, or
  standard revision (e.g. an EU AI Act update, a NIST AI RMF revision, a
  new state AI law) needs to be mapped to this project's existing
  frameworks and policies. Not for reviewing a specific system or vendor
  against the frameworks already in place — use the relevant assessment
  or review skill for that instead.
---

# Map an AI regulatory or standards development to the framework registry

Produces one advisory mapping for one development: not a legal opinion,
and not a substitute for the AI-governance-lead or legal review it
explicitly requires before any registry change is made.

This is the AI-governance domain's counterpart to
`map-regulatory-change`, reusing that skill's shape directly rather than
designing a third one (build-plan.md step 18): it doesn't evaluate an
institution's own activity, system, vendor, or inventory entry — it
ingests an external input and maps its impact against
`references/frameworks/index.md`, this project's own registry.
`frameworks_considered` here asks a different question than in its
sibling skills: not "does this framework apply to the institution" but
"does this development change what an already-registered framework
requires." The deliverable is a diff against the registry, not a finding
about a person or system.

The judgment happens here, in conversation, grounded in this skill's own
bundled `references/frameworks/`. No API call, no separate rater.
`scripts/regulatory_change.py` only validates the finished judgment
against the real framework ids, and renders it; it never assesses the
development's impact itself. Read the actual framework content before
determining impact — don't reason from memory of what a framework
"usually" requires.

Every path below is written as `${CLAUDE_SKILL_DIR}/...`, a substitution
Claude Code resolves to this skill's own directory regardless of whether
it's installed inside a full checkout of the source project, as a plugin,
or standalone. If that substitution doesn't happen in your current
environment, resolve the same path relative to the folder containing this
`SKILL.md` instead.

## Architecture

Everything this skill reads or runs at mapping time lives inside its own
directory:

- `references/frameworks/index.md` — the current framework registry, read
  in step 2 to decide which entries this development touches. Never
  hard-code a framework name anywhere in this procedure; read this file
  fresh every time, because the registry can grow or shrink independently
  of this `SKILL.md`.
- `references/frameworks/*/*.yaml` — the full content of every active
  framework: read the specific file(s) that might be impacted in full
  before concluding whether or how they're affected.
- `references/regulatory-change-schema.md` — the exact JSON shape step 3
  writes.
- `scripts/regulatory_change.py`, plus its sibling modules `language.py`,
  `concision.py`, `report.py` — the validate-and-render CLI step 3 calls.
  Dependency-free, stdlib-only Python (no `pyyaml`, no install step), so
  it runs with a plain `python3` wherever this skill ends up. Validates
  the written mapping against the real framework ids in `references/`,
  enforces the compliance/CST language boundary, flags anything unusually
  long, and renders the Markdown report. No `rubric.py`, no
  `baseline.py` — this shape uses neither.

This bundle is generated, not hand-edited, except for
`scripts/regulatory_change.py` itself and this file. In the source
project ([sgmuff/catholic-ai](https://github.com/sgmuff/catholic-ai)),
the rest is synced from the authored `frameworks/` directory by
`eval/sync_skill_bundle.py`; a test fails that project's CI if the bundle
ever drifts from what that script would produce. If you're working in
that project and just changed `frameworks/`, re-run the sync before
testing this skill — the bundle above, not the source directory, is what
actually gets read here.

## 1. Intake the development

Ask for (or accept as pasted text) the source of the development, the
specific citation if one exists, what changed in plain terms, and when it
was published or takes effect. This skill doesn't monitor anything on its
own — it works from what the user brings to the conversation.

## 2. Map impact against the registry

Read `${CLAUDE_SKILL_DIR}/references/frameworks/index.md` in full. For
each registered framework, ask whether this development changes what
that framework's `required_elements` actually require — not whether the
framework itself is generally relevant, but whether *this specific
development* touches it. Read the specific file(s) that might be
impacted in full before concluding either way. Record every framework
considered in `frameworks_considered`, including ones ruled not
impacted, so the record shows the reasoning happened rather than being
skipped.

## 3. Recommend actions, then write and render the record

For each impact found, recommend a specific action:

- **`register-new-framework`** — the development is a wholly new law or
  standard not covered by anything currently registered.
- **`update-required-element`** — an already-registered framework's
  entry needs a new or revised `required_elements` item to reflect the
  development.
- **`retire-framework`** — an already-registered framework has been
  repealed or superseded outright.
- **`no-action`** — considered and found not to require any registry
  change. Always record this explicitly when it's the outcome — an empty
  action list isn't a valid way to say nothing needs to change.

Write a JSON file matching
`${CLAUDE_SKILL_DIR}/references/regulatory-change-schema.md` exactly,
then run:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/regulatory_change.py --input <path-to-json> --out-dir <reports-dir>
```

`<reports-dir>` is `reports/` created next to wherever you're working in
this conversation, unless the user asks for somewhere else.

The script validates before it renders: every framework id real, at
least one recommended action present, a `framework_id` required for
`update-required-element`/`retire-framework` and rejected for
`register-new-framework`/`no-action`, and — enforcing this project's own
hard rule on Catholic language — the `compliance` field rejected if any
Catholic Social Teaching vocabulary has leaked into it. A non-zero exit
with "Could not build regulatory change mapping" on stderr lists every
problem found; fix the JSON and rerun rather than working around the
validation. A zero exit may still print non-fatal warnings on stderr
about a field running long — reread the flagged parts for restated or
padded text before treating the report as final.

## 4. Report back in plain language, briefly

This is an advisory draft, grounded in a working interpretation of the
frameworks actually applied above — not a legal opinion — and it requires
an AI-governance-lead or legal review before any registry change is
made. State which frameworks are impacted and the recommended action for
each, plainly and up front. This is a summary, not a restatement of the
full report. Close by pointing the user to the rendered report file for
the full basis. If the user asks you to actually make the recommended
registry change (e.g. add a `required_elements` entry to a framework
file), that's a separate, explicit step outside this skill — this skill
only produces the recommendation.

## Human oversight and escalation

This skill never edits `frameworks/` on anyone's behalf and never makes a
final determination that a development requires or doesn't require a
registry change — it drafts a finding for a named accountable person to
review and act on. Escalate plainly, rather than only noting in the
report, a development that appears to newly prohibit or restrict AI
practices already in use, since that carries operational urgency beyond
a routine registry update.

## Grounding

Personalism and the dignity of the human person ground why the framework
registry itself needs active upkeep — a stale registry quietly
under-serves the very people affected by the AI systems these frameworks
govern, even though nothing about the institution's own systems has
changed. The primacy of human judgment over automated determination
grounds why a change that affects human-oversight obligations gets
flagged with particular care. This reasoning belongs in
`cst_reflection`, alongside the compliance findings, never inside them.
