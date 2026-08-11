# Assessment JSON schema

The exact shape `scripts/assessment.py --input <path> --out-dir <reports-dir>`
validates and renders. Write this JSON before calling the script — the script
never scores anything itself, it only checks the judgment below is internally
consistent.

## Top level

- `title` (string, required) — a short, specific name for this activity (e.g.
  "Parish bulletin sign-up form"). Used to name the rendered report file.
- `subject` (object, required)
- `frameworks_considered` (array, required)
- `ratings` (array, required) — exactly one entry per dimension in
  `${CLAUDE_SKILL_DIR}/references/rubric/criteria.md`
- `compliance` (string, required)
- `cst_reflection` (string, required)

## `subject`

- `description` (string, required) — what's being built or changed.
- `purpose` (string, required) — why this data is collected or processed.
- `personal_data` (array of strings) — the specific data elements involved.
- `systems` (array of strings) — the technical systems involved.
- `recipients` (array of strings) — who receives or can access the data,
  internal or external.
- `retention` (string, required) — how long the data is kept and what
  happens after. Never empty; the validator checks this field explicitly.
- `institution_context` (string) — the kind of institution this activity
  belongs to (a diocese, a hospital, a university, a company...) — useful
  for reasoning about framework applicability in step 2.

## `frameworks_considered`

One entry per framework read in step 2 — **including ones ruled
inapplicable**, so the record shows the reasoning actually happened rather
than being skipped.

- `id` (string, required) — must be an `id` from
  `${CLAUDE_SKILL_DIR}/references/frameworks/index.md`. An invented id is
  rejected.
- `applicable` (boolean, required)
- `basis` (string, required) — the specific fact that makes this framework
  apply or not apply. Never empty.

## `ratings`

Exactly one entry per dimension id in
`${CLAUDE_SKILL_DIR}/references/rubric/criteria.md` — no more, no fewer, no
duplicates.

- `dimension_id` (string, required) — must match a rubric dimension id
  exactly.
- `score` (integer 1-5, required)
- `rationale` (string, required) — the specific fact that drove the score.
  One to three sentences (§2.2 of this project's build plan) — never restate
  the rubric criterion's own description back.
- `mitigation` (string or `null`) — required and non-empty whenever `score`
  is below the rubric's stated passing threshold; `null` otherwise.
- `ideal` (string, required) — always present, regardless of score.
- `contested` (boolean, required) — `true` only for a genuine tension
  between two dimensions on this specific activity, explained in the
  rationale — not a substitute for a low score.

## `compliance`

One string. Regulatory findings only, in the applicable framework(s)' own
register — exact terms of art, citations, statutory verbs. Never Catholic
Social Teaching vocabulary; `scripts/language.py` rejects the assessment if
any leaks in. Concision-linted against how many frameworks were actually
marked `applicable`.

## `cst_reflection`

One string. The Catholic grounding — personalism, subsidiarity, solidarity,
the primacy of human judgment — layered alongside the compliance findings,
never inside them. Concision-linted against a flat guideline.
