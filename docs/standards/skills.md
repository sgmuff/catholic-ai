# Skills standard

Claude Skills in this repository follow the open [Agent Skills specification](https://agentskills.io/specification). That spec is the floor: a skill is a directory containing a `SKILL.md` file with required `name` and `description` frontmatter, optionally alongside `scripts/`, `references/`, and `assets/`. Read the spec before writing one — what follows here is only what this repository adds on top of it.

## Where a skill lives

Skills live under `.claude/skills/<skill-name>/`, not a plain `skills/` at the top level — `.claude/skills/` is what Claude Code actually scans to discover and invoke a skill by name. A skill sitting anywhere else might satisfy the Agent Skills spec, but Claude Code won't find it.

Skills default to `.claude/skills/<skill-name>/` at the repository root, because the useful ones are the ones reused across projects: a skill that assesses an AI system against CST and a recognized risk framework, or one that drafts a model-documentation record, is exactly as useful to a diocese as to a secular hospital system — there's no confessional/secular split to route it through.

A skill lives inside a project's own `<project-name>/.claude/skills/` directory only when it is genuinely specific to that project — a template-filling script tied to one institution's exact intake form, say, or one wired tightly to that project's own CLI and file layout. That's the exception, and a skill placed there should have a one-line note in the project's README explaining why it isn't shared.

## Naming

Skill names are kebab-case and verb-first where the skill performs an action, matching the spec's constraint that `name` is lowercase, hyphen-separated, and matches the containing folder:

- `assess-ai-risk-cst` — evaluate a system or proposal against CST and a mapped risk framework
- `draft-model-card` — produce a model-documentation record
- `review-data-retention-policy` — check a policy against the retention baseline in `docs/standards/security-and-privacy.md`

Avoid vague names (`helper`, `utils`, `ai-tools`) that don't tell an agent — or a person browsing `.claude/skills/` — what the skill actually does.

## Description quality

Per the spec, `description` has to state both what the skill does and when to use it, in language specific enough that an agent can tell it apart from a neighboring skill. Write it the way a colleague would explain the skill in one sentence, not the way a product page would advertise it:

- **Good:** "Evaluates an AI system proposal against Catholic Social Teaching principles and a mapped NIST AI RMF / ISO 42001 category, producing a structured findings memo. Use when reviewing a new AI initiative before it's approved."
- **Poor:** "Helps you think about AI ethics."

No promotional language — "powerful," "seamless," "revolutionary" — has any place in a `SKILL.md`. This is a working tool, not a pitch.

## Validation

Before a skill is merged, validate it with the reference tool:

```
skills-ref validate ./.claude/skills/<skill-name>
```

`.github/workflows/ci.yml` runs this same check against every `SKILL.md` it finds anywhere in the repository, so a skill that fails validation fails CI regardless of whether it's shared or project-local.

## Size discipline

Keep `SKILL.md` itself under roughly 500 lines. If a skill needs more than that to explain itself, the excess belongs in `references/`, loaded by the agent only when it's actually needed — that's the progressive-disclosure design the spec is built around, and it's what keeps a skill cheap to keep on hand even when it's rarely used.
