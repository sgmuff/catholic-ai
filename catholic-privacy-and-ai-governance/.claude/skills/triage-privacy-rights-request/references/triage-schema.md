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

The single deadline that controls the response. Always present — even
when no registered framework actually applies, a request still gets a
plainly-stated date, per step 4's "state the governing deadline plainly
and up front."

- `statutory` (boolean, required) — `true` when a registered framework
  actually imposes this deadline; `false` when none of the frameworks
  marked `applicable` in `frameworks_considered` do, and this is an
  internal, non-binding target instead. `false` is only valid when
  `frameworks_considered` has **no** entry marked `applicable` — if a
  framework does apply, its deadline governs and can't be sidestepped.
- `framework_id` (string or `null`) — when `statutory: true`, required and
  must be marked `applicable` in `frameworks_considered` (chosen in step 2
  as the shortest applicable deadline, when more than one framework
  applies). When `statutory: false`, must be `null` — an internal target
  can't be attributed to a framework that doesn't actually govern it, the
  same discipline §2.1 already applies to the `compliance` field.
- `citation` (string, required) — when `statutory: true`, the specific
  statutory provision, e.g. `Art. 12(3)`. When `statutory: false`, a short
  label naming this as institutional practice rather than law, e.g.
  "Internal target — no applicable framework imposes a deadline."
- `response_due` (string, required) — ISO date, calculated from
  `request.received_date`. When `statutory: true`, per the governing
  provision's stated period. When `statutory: false`, per whatever
  internal practice or benchmark the institution uses. Must not fall
  before `received_date` either way.
- `basis` (string, required) — the calculation shown: the stated period
  and the arithmetic from the received date, either way. When
  `statutory: false`, may note that the target's length was calibrated
  against a real framework's comparable period for reasonableness, but
  must say plainly that framework doesn't govern this request — an
  analogy, not an authority.

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
