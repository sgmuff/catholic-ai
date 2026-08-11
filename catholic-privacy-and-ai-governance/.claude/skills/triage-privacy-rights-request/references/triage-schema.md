# Triage JSON schema

The exact shape `scripts/triage.py --input <path> --out-dir <reports-dir>`
validates and renders. Write this JSON before calling the script — the
script never classifies or calculates anything itself, it only checks the
judgment below is internally consistent.

## Top level

- `title` (string, required) — a short, specific name for this request
  (e.g. "Access request from a returning parishioner"). Used to name the
  rendered report file.
- `request` (object, required)
- `frameworks_considered` (array, required)
- `governing_deadline` (object, required)
- `gaps` (array) — may be empty once nothing is outstanding.
- `compliance` (string, required)
- `cst_reflection` (string, required)

## `request`

- `description` (string, required) — what the requester asked for, in
  their own terms.
- `request_type` (string, required) — access, deletion, correction,
  portability, restriction, or objection.
- `channel` (string) — how the request arrived.
- `received_date` (string, required) — ISO date (`YYYY-MM-DD`) the request
  was received. Anchors `governing_deadline.response_due`.
- `requester_context` (string) — who's asking and their relationship to
  the data (a parishioner, an employee, a student...).

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

## `governing_deadline`

The single deadline that controls the response, chosen in step 2 from
among every framework marked `applicable` above (the shortest applicable
deadline governs when more than one applies).

- `framework_id` (string, required) — must be marked `applicable` in
  `frameworks_considered`; a deadline can't be governed by a framework
  ruled inapplicable.
- `citation` (string, required) — the specific provision, e.g. `Art.
  12(3)`.
- `response_due` (string, required) — ISO date, calculated from
  `request.received_date` per that provision's stated period. Must not
  fall before `received_date`.
- `basis` (string, required) — the calculation shown: which provision, its
  stated period, and the arithmetic from the received date.

## `gaps`

Anything still needed before the request can be answered — most often
identity verification, but also scope clarification or an exemption
determination. Empty once nothing is outstanding.

- `id` (string, required)
- `description` (string, required)
- `blocking` (boolean, required) — `true` if the response deadline clock
  is effectively paused on this gap; `false` if it can be resolved in
  parallel without delaying the response.

## `compliance`

One string. Regulatory findings only, in the applicable framework(s)' own
register — exact terms of art, citations, statutory verbs. Never Catholic
Social Teaching vocabulary; `scripts/language.py` rejects the triage
record if any leaks in. Concision-linted against how many frameworks were
actually marked `applicable`.

## `cst_reflection`

One string. The Catholic grounding — personalism, subsidiarity,
solidarity — layered alongside the compliance findings, never inside them.
Concision-linted against a flat guideline.
