# Assessment JSON schema

The exact shape `scripts/assessment.py --input <path> --out-dir <reports-dir>`
validates and renders. Identical schema to `draft-privacy-impact-assessment`'s
own — this skill scores the same rubric, because a notice has to describe the
practice honestly, and the same seven dimensions that assess whether a
practice is sound are what determine what the notice actually needs to
disclose. Write this JSON before calling the script — the script never scores
anything itself, it only checks the judgment below is internally consistent.

## Top level

- `title` (string, required) — a short, specific name for the change in
  practice being assessed (e.g. "Adding SMS reminders to the appointment
  system"). Used to name the rendered report file.
- `subject` (object, required)
- `frameworks_considered` (array, required)
- `ratings` (array, required) — exactly one entry per dimension in
  `${CLAUDE_SKILL_DIR}/references/rubric/criteria.md`
- `compliance` (string, required)
- `cst_reflection` (string, required)

## `subject`

- `description` (string, required) — what's changing about the practice.
- `purpose` (string, required) — why the underlying practice exists.
- `personal_data` (array of strings) — the specific data elements involved.
- `systems` (array of strings) — the technical systems involved.
- `recipients` (array of strings) — who receives or can access the data.
- `retention` (string, required) — how long the data is kept and what
  happens after. Never empty.
- `institution_context` (string) — the kind of institution this practice
  belongs to.

## `frameworks_considered`, `ratings`, `compliance`, `cst_reflection`

Identical rules to `draft-privacy-impact-assessment`'s own schema — see
that skill's `references/assessment-schema.md` if you need the field-level
detail. The only difference this skill introduces is what happens *after*
the assessment validates and renders (step 5 of `SKILL.md`): drafting the
actual notice language, which is not part of this JSON and is not rendered
by the script — see `SKILL.md` for why.
