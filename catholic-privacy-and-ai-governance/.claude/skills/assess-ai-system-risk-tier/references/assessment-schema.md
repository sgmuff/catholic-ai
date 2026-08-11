# Assessment JSON schema

The exact shape `scripts/assessment.py --input <path> --out-dir <reports-dir>`
validates and renders. Write this JSON before calling the script — the script
never scores anything itself, it only checks the judgment below is internally
consistent. Identical shape to the privacy-domain flagship's own schema — the
field meanings below are adapted for an AI system rather than a data-processing
activity, but the structure is deliberately the same.

## Top level

- `title` (string, required) — a short, specific name for the AI system
  (e.g. "Patient scheduling triage assistant"). Used to name the rendered
  report file.
- `subject` (object, required)
- `frameworks_considered` (array, required)
- `ratings` (array, required) — exactly one entry per dimension in
  `${CLAUDE_SKILL_DIR}/references/rubric/ai-criteria.md`
- `compliance` (string, required)
- `cst_reflection` (string, required)

## `subject`

- `description` (string, required) — what the system is and does.
- `purpose` (string, required) — why it exists; what decision or output it
  produces.
- `personal_data` (array of strings) — any personal data the system uses or
  produces, if applicable; an AI system that never touches personal data
  can leave this empty.
- `systems` (array of strings) — the technical systems and any third-party
  models or components involved.
- `recipients` (array of strings) — who receives or acts on the system's
  output, internal or external.
- `retention` (string, required) — how long the system's inputs, outputs,
  or logs are kept and what happens after. Never empty — the validator
  checks this field explicitly. If the system genuinely retains nothing,
  say so explicitly rather than leaving it blank.
- `institution_context` (string) — the kind of institution deploying the
  system, useful for reasoning about framework applicability.

## `frameworks_considered`

One entry per framework read during intake — **including ones ruled
inapplicable**, so the record shows the reasoning actually happened rather
than being skipped. The EU AI Act risk-tier determination (prohibited,
high-risk, limited-risk, or minimal-risk) and its basis belong here, stated
as the compliance finding it is — see `compliance` below, not a separate
field.

- `id` (string, required) — must be an `id` from
  `${CLAUDE_SKILL_DIR}/references/frameworks/index.md`. An invented id is
  rejected.
- `applicable` (boolean, required)
- `basis` (string, required) — the specific fact that makes this framework
  apply or not apply, and for the EU AI Act specifically, the risk tier and
  the Annex III category (or prohibited-practice category) it matches, if
  any. Never empty.

## `ratings`

Exactly one entry per dimension id in
`${CLAUDE_SKILL_DIR}/references/rubric/ai-criteria.md` — no more, no fewer,
no duplicates.

- `dimension_id` (string, required) — must match a rubric dimension id
  exactly.
- `score` (integer 1-5, required)
- `rationale` (string, required) — the specific fact that drove the score.
  One to three sentences — never restate the rubric criterion's own
  description back.
- `mitigation` (string or `null`) — required and non-empty whenever `score`
  is below the rubric's stated passing threshold; `null` otherwise.
- `ideal` (string, required) — always present, regardless of score.
- `contested` (boolean, required) — `true` only for a genuine tension
  between two dimensions on this specific system, explained in the
  rationale — not a substitute for a low score.

## `compliance`

One string. Regulatory findings only, in the applicable framework(s)' own
register — exact terms of art, article citations, statutory verbs. This is
where the EU AI Act risk-tier determination is stated as a finding (e.g.
"This system falls within Annex III(4)(a) as an employment-related AI
system, making it high-risk under Art. 6"), not a separate structured
field. Never Catholic Social Teaching vocabulary; `scripts/language.py`
rejects the assessment if any leaks in. Concision-linted against how many
frameworks were actually marked `applicable`.

## `cst_reflection`

One string. The Catholic grounding — personalism, subsidiarity, solidarity,
the primacy of human judgment — layered alongside the compliance findings,
never inside them. Concision-linted against a flat guideline.
