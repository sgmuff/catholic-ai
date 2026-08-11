# Assessment JSON schema

The exact shape `scripts/assessment.py --input <path> --out-dir <reports-dir>`
validates and renders. Identical schema to `assess-ai-system-risk-tier`'s
own — this skill scores the same rubric, because a model card has to
describe the system honestly, and the same seven dimensions that assess
whether a system is sound are what determine what the card actually needs
to disclose. Write this JSON before calling the script — the script never
scores anything itself, it only checks the judgment below is internally
consistent.

## Top level

- `title` (string, required) — a short, specific name for the AI system
  being documented (e.g. "Parking Permit Waitlist Ranker"). Used to name
  the rendered report file.
- `subject` (object, required)
- `frameworks_considered` (array, required)
- `ratings` (array, required) — exactly one entry per dimension in
  `${CLAUDE_SKILL_DIR}/references/rubric/ai-criteria.md`
- `compliance` (string, required)
- `cst_reflection` (string, required)

## `subject`

- `description` (string, required) — what the system does.
- `purpose` (string, required) — why the system exists and who it serves.
- `personal_data` (array of strings) — the data elements the system uses,
  if any.
- `systems` (array of strings) — the technical systems the model or
  feature runs in.
- `recipients` (array of strings) — who receives or acts on the system's
  output.
- `retention` (string, required) — how long inputs, outputs, or training
  data derived from this use are kept. Never empty.
- `institution_context` (string) — the kind of institution deploying the
  system.

## `frameworks_considered`, `ratings`, `compliance`, `cst_reflection`

Identical rules to `assess-ai-system-risk-tier`'s own schema — see that
skill's `references/assessment-schema.md` if you need the field-level
detail. The only difference this skill introduces is what happens *after*
the assessment validates and renders (step 5 of `SKILL.md`): drafting the
actual model-card document, which is not part of this JSON and is not
rendered by the script — see `SKILL.md` for why.
