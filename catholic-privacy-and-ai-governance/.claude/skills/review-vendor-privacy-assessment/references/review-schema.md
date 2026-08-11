# Review JSON schema

The exact shape `scripts/review.py --input <path> --out-dir <reports-dir>`
validates and renders. Write this JSON before calling the script — the
script never checks the vendor's documentation itself, it only checks the
judgment below is internally consistent.

## Top level

- `title` (string, required) — a short, specific name for this review
  (e.g. "Annual review of MailerParish, Inc."). Used to name the rendered
  report file.
- `vendor` (object, required)
- `frameworks_considered` (array, required)
- `baseline_items` (array, required) — exactly one entry per item in
  `${CLAUDE_SKILL_DIR}/references/baseline/privacy-vendor.md`
- `remediation_commitments` (array) — may be empty once nothing is open.
- `reassessment_due` (string, required) — ISO date (`YYYY-MM-DD`).
- `overall_risk` (object, required)
- `compliance` (string, required)
- `cst_reflection` (string, required)

## `vendor`

- `name` (string, required)
- `description` (string, required) — what the vendor does and what
  institutional data or systems it touches.
- `service_provided` (string) — the specific service under contract.

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

## `baseline_items`

Exactly one entry per item id in
`${CLAUDE_SKILL_DIR}/references/baseline/privacy-vendor.md` — no more, no
fewer, no duplicates.

- `id` (string, required) — must match a baseline item id exactly.
- `status` (string, required) — `satisfied`, `partial`, or `missing`.
- `evidence` (string or `null`) — required and non-empty whenever `status`
  is `satisfied` or `partial`; `null` when `missing`.
- `gap` (string or `null`) — required and non-empty whenever `status` is
  `partial` or `missing`; `null` when `satisfied`.

## `remediation_commitments`

One entry per commitment the vendor has made to close a gap. Empty once
nothing is open.

- `id` (string, required)
- `description` (string, required) — what the vendor committed to.
- `target_date` (string, required) — ISO date the commitment is due.
- `status` (string, required) — `open` or `complete`.

## `overall_risk`

- `level` (string, required) — one of `low`, `moderate`, `high`,
  `critical`.
- `rationale` (string, required) — the specific baseline gaps and
  mitigating factors (responsiveness, an open remediation commitment with
  a near-term date, alternative controls) that drove the level.

## `compliance`

One string. Regulatory findings only, in the applicable framework(s)' own
register — exact terms of art, citations, statutory verbs. Never Catholic
Social Teaching vocabulary; `scripts/language.py` rejects the review if
any leaks in. Concision-linted against how many frameworks were actually
marked `applicable`.

## `cst_reflection`

One string. The Catholic grounding — personalism, subsidiarity,
solidarity — layered alongside the compliance findings, never inside
them. Concision-linted against a flat guideline.
