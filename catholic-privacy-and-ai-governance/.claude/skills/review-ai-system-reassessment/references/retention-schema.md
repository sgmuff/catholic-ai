# Reassessment entry JSON schema

The exact shape `scripts/retention.py --input <path> --out-dir <reports-dir>`
validates and renders. Write this JSON before calling the script — the
script never decides the verdict itself, it only checks the judgment
below is internally consistent.

This is the smallest schema in the family, deliberately: one inventoried
AI system, checked once, producing one verdict — not a score, not a list
of deadlines, not a checklist.

## Top level

- `title` (string, required) — a short, specific name for this system
  (e.g. "Parking Permit Waitlist Ranker"). Used to name the rendered
  report file.
- `entry` (object, required)
- `frameworks_considered` (array, required)
- `verdict` (object, required)
- `compliance` (string, required)
- `cst_reflection` (string, required)

## `entry`

- `description` (string, required) — what this AI system does.
- `category` (string, required) — the kind of thing this entry is (e.g.
  "AI system", "AI-enabled feature").
- `purpose` (string, required) — why it exists.
- `last_reviewed_date` (string, required) — ISO date (`YYYY-MM-DD`) this
  system was last assessed or its documentation last confirmed current.

## `frameworks_considered`

One entry per framework read in step 1 — **including ones ruled
inapplicable**, so the record shows the reasoning actually happened rather
than being skipped.

- `id` (string, required) — must be an `id` from
  `${CLAUDE_SKILL_DIR}/references/frameworks/index.md`. An invented id is
  rejected.
- `applicable` (boolean, required)
- `basis` (string, required) — the specific fact that makes this framework
  apply or not apply. Never empty.

## `verdict`

- `action` (string, required) — one of `current`, `needs-review`,
  `needs-update`, `retire`.
- `rationale` (string, required) — the specific facts that drove the
  verdict, grounded in the system's own defined re-evaluation interval
  (set by its risk tier) and what `last_reviewed_date` shows about
  whether that interval has lapsed.
- `target_date` (string or `null`) — required and a valid ISO date
  whenever `action` is anything other than `current`; `null` (or an
  optional valid date) when `action` is `current`.

## `compliance`

One string. Regulatory findings only, in the applicable framework(s)' own
register — exact terms of art, citations, statutory verbs. Never Catholic
Social Teaching vocabulary; `scripts/language.py` rejects the entry if
any leaks in. Concision-linted against how many frameworks were actually
marked `applicable`.

## `cst_reflection`

One string. The Catholic grounding — personalism, subsidiarity,
solidarity, the primacy of human judgment — layered alongside the
compliance findings, never inside them. Concision-linted against a flat
guideline.
