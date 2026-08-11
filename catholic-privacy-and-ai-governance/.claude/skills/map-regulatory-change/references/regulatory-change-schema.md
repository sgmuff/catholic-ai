# Regulatory change JSON schema

The exact shape `scripts/regulatory_change.py --input <path> --out-dir <reports-dir>`
validates and renders. Write this JSON before calling the script — the
script never assesses the development's impact itself, it only checks the
judgment below is internally consistent.

Unlike every other skill in this family, this one doesn't evaluate an
institution's own activity, system, vendor, or inventory entry — it
ingests an external input (a pasted regulatory or standards development)
and maps its impact against `references/frameworks/index.md`, this
project's own registry. `frameworks_considered` asks a different
question here than in its sibling skills: not "does this framework apply
to the institution" but "does this development change what an
already-registered framework requires" — the field is named `impacted`,
not `applicable`, to keep that distinction honest.

## Top level

- `title` (string, required) — a short, specific name for this
  development (e.g. "CPPA risk-assessment regulations take effect").
  Used to name the rendered report file.
- `development` (object, required)
- `frameworks_considered` (array, required)
- `recommended_actions` (array, required) — never empty; record
  `no-action` explicitly if nothing needs to change.
- `compliance` (string, required)
- `cst_reflection` (string, required)

## `development`

- `source` (string, required) — who issued this (a regulator, a
  legislature, a standards body).
- `citation` (string) — the specific instrument (a bill number, a
  regulation section, a standard revision).
- `summary` (string, required) — what changed, in plain terms.
- `published_date` (string, required) — ISO date (`YYYY-MM-DD`) the
  development was published or took effect.

## `frameworks_considered`

One entry per framework read in step 1 — **including ones ruled not
impacted**, so the record shows the reasoning actually happened rather
than being skipped.

- `id` (string, required) — must be an `id` from
  `${CLAUDE_SKILL_DIR}/references/frameworks/index.md`. An invented id is
  rejected.
- `impacted` (boolean, required)
- `basis` (string, required) — the specific fact that makes this
  framework impacted or not. Never empty.

## `recommended_actions`

At least one entry — `no-action` is a legitimate, explicit outcome, not
an empty list.

- `id` (string, required)
- `type` (string, required) — one of `register-new-framework`,
  `update-required-element`, `retire-framework`, `no-action`.
- `framework_id` (string or `null`) — required and must be a known
  framework id when `type` is `update-required-element` or
  `retire-framework`; must be `null` when `type` is
  `register-new-framework` or `no-action` (there's no existing id to
  reference in either case).
- `description` (string, required) — the specific change recommended.

## `compliance`

One string. Regulatory findings only, in the applicable framework(s)' own
register — exact terms of art, citations, statutory verbs. Never Catholic
Social Teaching vocabulary; `scripts/language.py` rejects the record if
any leaks in. Concision-linted against how many frameworks were actually
marked `impacted`.

## `cst_reflection`

One string. The Catholic grounding — personalism, subsidiarity,
solidarity — layered alongside the compliance findings, never inside
them. Concision-linted against a flat guideline.
