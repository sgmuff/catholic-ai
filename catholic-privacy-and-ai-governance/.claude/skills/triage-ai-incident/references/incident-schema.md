# Incident JSON schema

The exact shape `scripts/incident.py --input <path> --out-dir <reports-dir>`
validates and renders. Write this JSON before calling the script — the
script never assesses severity, identifies obligations, or calculates
anything itself, it only checks the judgment below is internally
consistent.

An AI incident can trigger several independent, simultaneous
notification or reporting obligations to different audiences at once (a
market surveillance authority under one framework, an internal governance
body under another) — none of which "governs" over the others.
`notification_obligations` below is a list for exactly that reason; there
is no single governing-deadline field here.

## Top level

- `title` (string, required) — a short, specific name for this incident.
  Used to name the rendered report file.
- `incident` (object, required)
- `frameworks_considered` (array, required)
- `severity` (object, required)
- `notification_obligations` (array) — may be empty if nothing applies.
- `gaps` (array) — may be empty once nothing is outstanding.
- `escalation` (object, required)
- `compliance` (string, required)
- `cst_reflection` (string, required)

## `incident`

- `description` (string, required) — what the AI system did, what a human
  relying on it did as a result, and the known downstream impact.
- `discovered_date` (string, required) — ISO date (`YYYY-MM-DD`) the
  incident was discovered. Anchors every `notification_obligations[].due_date`.
- `affected_systems` (array of strings) — the AI system(s) and any
  surrounding systems involved.
- `data_types` (array of strings) — the categories of data or output
  involved, if relevant (e.g. training data, a generated decision).
- `individuals_affected_estimate` (integer) — a best current estimate;
  refine as scope is confirmed.

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

## `severity`

- `level` (string, required) — one of `low`, `moderate`, `high`,
  `critical`.
- `rationale` (string, required) — the specific facts that drove the
  level: whether the incident meets the EU AI Act's "serious incident"
  definition (death or serious harm to health, critical-infrastructure
  disruption, a fundamental-rights infringement, or serious harm to
  property/environment), the scale of individuals affected, and whether
  harm has actually materialized versus remaining a possibility.

## `notification_obligations`

One entry per independent notification or reporting duty triggered by an
applicable framework — not a single "governing" one. A single incident
can have more than one of these at once (e.g. a market-surveillance-
authority report under the EU AI Act *and* an internal governance-body
report under an adopted NIST AI RMF profile).

- `id` (string, required)
- `framework_id` (string, required) — must be marked `applicable` in
  `frameworks_considered`; an obligation can't come from a framework ruled
  inapplicable.
- `audience` (string, required) — who must be notified (a market
  surveillance authority, an internal AI governance body, affected
  individuals...).
- `citation` (string, required) — the specific provision, e.g. `Art.
  73(2)`.
- `due_date` (string, required) — ISO date, calculated from
  `incident.discovered_date` per that provision's stated period. Must not
  fall before `discovered_date`.
- `basis` (string, required) — the calculation shown: which provision,
  which severity tier it falls under, and the arithmetic from the
  discovery date.

## `gaps`

Anything still needed before every applicable obligation can be
discharged — most often confirming whether a causal link between the AI
system and the harm has been established (the EU AI Act's reporting clock
starts there, not at bare discovery), but also containment status or
scope confirmation. Empty once nothing is outstanding.

- `id` (string, required)
- `description` (string, required)
- `blocking` (boolean, required) — `true` if it blocks meeting a
  notification deadline; `false` if it can be resolved in parallel.

## `escalation`

- `required` (boolean, required) — whether this incident meets the
  severity, safety, legal, or executive-reporting threshold for
  escalation.
- `rationale` (string, required) — the specific threshold met, or why none
  was met.

## `compliance`

One string. Regulatory findings only, in the applicable framework(s)' own
register — exact terms of art, citations, statutory verbs. Never Catholic
Social Teaching vocabulary; `scripts/language.py` rejects the incident
record if any leaks in. Concision-linted against how many frameworks were
actually marked `applicable`.

## `cst_reflection`

One string. The Catholic grounding — personalism, subsidiarity,
solidarity, the primacy of human judgment — layered alongside the
compliance findings, never inside them. Concision-linted against a flat
guideline.
