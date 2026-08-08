# CST Finding

A schema, a graded rubric, and an advisory eval harness that let a team run an AI system against Catholic Social Teaching before it ships — the translation layer CST has never had, the way GDPR Art. 35 turned "protect fundamental rights" into a mandatory, auditable DPIA.

It started life as `cst-model-constitution`. The rename matters and stays visible here: "constitution" implied this shapes model *behavior* the way training-time alignment does. Almost no institution using this repo trains foundation models; they call a vendor API. What this repo does is *audit and advise*, not train. Overclaiming that distinction is how a governance tool turns into ethics-washing — which is exactly what the section below exists to prevent.

Renamed again, from `cst-alignment-rubric`, to match the Claude Skill that does the actual work: shorter, and named for what the tool produces — one advisory finding per subject, per `rubric/criteria.md` — rather than restating that it's a rubric, which the Non-Goals below already qualify heavily.

## Non-Goals

- **Not a substitute for training-time alignment.** It does not shape model weights. It evaluates the behavior of systems already built or bought.
- **Not a hard CI gate by default.** LLM output is nondeterministic and LLM-as-judge scoring is unreliable on value-laden criteria — a hard block produces flaky builds and false confidence. Default behavior is advisory: flag, route to human review, log.
- **Not a canonical magisterial interpretation.** Competent theologians disagree on contested applications (immigration enforcement and solidarity, labor structures and subsidiarity). The rubric documents a working interpretation, dated and versioned, not "the" Catholic position.
- **Not a certification or marketing claim.** "Passed the rubric" is not a compliance stamp. CI output is worded as advisory, not pass/fail, to make misuse harder.
- **Not a replacement for pastoral or human judgment.** `rubric/known-tensions.md` exists precisely to keep this limitation visible rather than buried.

## Audience

Any institution — Catholic or secular — that has to decide whether an AI system it's about to deploy or has already deployed holds up against Catholic Social Teaching: a diocese or Catholic hospital reviewing a vendor tool, or a secular compliance officer or board who wants the reasoning behind CST's conclusions without first being persuaded of the theology. One rubric, one voice, for both — see [`../CONTRIBUTING.md`](../CONTRIBUTING.md) for why this repository doesn't split confessional and secular readers into separate tracks.

## Status

`draft` (beta). All eight principles and the non-negotiables bright-line list are drafted and cited, and the assessment tool (`eval/assessment.py` + the `cst-finding` skill) runs end to end — but every word of principle content is **unreviewed**: no named theological reviewer has signed off on it. See [Definition of done (v0.1)](#definition-of-done-v01) for what "active" requires.

As of 2026-08-08, this project does not gate `principles/` or `rubric/` changes on a project-level theological reviewer's sign-off (see `CONTRIBUTING.md` "Beta status"); ordinary technical review applies, and substantive changes are still dated and logged in `docs/theological-review-log.md`. In place of a one-time project-level sign-off, every report the tool generates recommends review by the using parish's own pastor or someone else there well versed in Catholic theology before a finding is acted on. Content written before and after this change is equally unreviewed in the sense of "no named theologian has checked it" and must say so wherever it's shown.

## Grounding

Eight principles, each cited directly against *Magnifica Humanitas* paragraph numbers and the wider CST tradition: personalism, common good, subsidiarity, solidarity, universal destination of goods, preferential option for the poor, dignity and inviolability of life, and social justice (added after *Magnifica Humanitas* named it as one of its own headline principles — see `docs/magnifica-humanitas-findings.md`). The bright-line gate and all eight graded principles additionally cite the Catechism of the Catholic Church (see `docs/ccc-citation-map.md`); the bright-line gate also cites Evangelium Vitae, and each graded principle cites one further USCCB-foundational-documents-list encyclical. `docs/usccb-foundational-documents-index.md` catalogues the full USCCB list and what remains uncited (Tier C). Where relevant, a principle's rubric criteria are also mapped to NIST AI RMF, ISO/IEC 42001, and the EU AI Act's risk tiers, per [`docs/standards/architecture.md`](../docs/standards/architecture.md#reference-frameworks) — but CST is the throughline those frameworks are judged against, not a parallel authority alongside it.

## How it works, in plain terms

1. **Write down the values.** Each of the eight principles gets its own file: what it means in plain terms, where it comes from in Church teaching, and which other principles it tends to clash with. A separate, smaller file — `principles/non-negotiables.yaml` — holds the handful of things CST treats as settled, not as one factor to weigh: direct abortion, euthanasia, direct killing of the innocent, systemic wage theft by design, and facilitation of trafficking or sexual exploitation — the last two added from the Catechism's "sins that cry to heaven" (CCC 1867) and Evangelium Vitae §3.
2. **Bring a subject, in conversation.** The `cst-finding` Claude Skill takes either of two things: someone deciding whether to build, buy, or keep running a specific AI use describes it — what it does, who it affects, what it decides — with follow-up questions only where the description is genuinely unclear; or someone with an actual prompt and response from a deployed AI system pastes them in verbatim to have that specific interaction audited after the fact.
3. **Check the bright line first.** Before anything gets scored, the subject — the described use, or what the response actually said or did — is checked against `principles/non-negotiables.yaml`. If it matches, the assessment says so plainly and stops there — see [Non-Goals](#non-goals) and `rubric/criteria.md`.
4. **Otherwise, score all eight principles.** Each principle gets a 1-5 score grounded in that principle's own description, a real rationale, and — for anything scoring 3 or below — a specific mitigation, not generic advice. A case where two good principles genuinely disagree gets flagged `contested`, not averaged into a single number.
5. **Hand back a report, not a verdict.** Nothing here is a certification. A low score or even a bright-line match is a finding for a person to act on.
6. **Keep a real person accountable for the definitions.** Changing what a principle or non-negotiable file says requires sign-off from a named theologian, the same way changing a contract needs a lawyer's, not just an engineer's opinion.

## Architecture

Three layers, each independent of the other two, wired together by one skill:

**The rubric's definitions — `principles/`.** The eight graded principle files (`personalism.yaml`, `common-good.yaml`, `subsidiarity.yaml`, `solidarity.yaml`, `universal-destination-of-goods.yaml`, `preferential-option-for-the-poor.yaml`, `dignity-and-inviolability-of-life.yaml`, `social-justice.yaml`) each follow the shape `schema.yaml` documents — `id`, `magisterial_citations`, a plain-language `description`, `tensions` with other principles, and worked `scenarios`. `non-negotiables.yaml` is the separate, smaller bright-line gate, checked before any of the eight get scored — see Non-Goals above for why it's kept deliberately short. Nothing in `principles/` is code; it's the actual theological content, and it's what a theological reviewer signs off on, not `eval/` or the skill.

**The rubric's algorithm — `rubric/`.** `criteria.md` is the source of truth for the two-stage process (bright-line gate, then graded rubric) that both the skill's procedure and `eval/`'s validation logic implement — if either ever drifts from what `criteria.md` says, `criteria.md` wins. `known-tensions.md` is the stress-test library of worked hard cases (two good principles genuinely in conflict) that back a `contested: true` finding instead of forcing a case to a single misleading number.

**The orchestration — `.claude/skills/cst-finding/`.** The `cst-finding` Claude Skill is where the actual judgment happens, in conversation — it interviews the user (or takes a prompt/response pair to audit), reasons through the two-stage rubric, and writes the finished judgment as JSON matching its own `references/assessment-schema.md`. It never calls a separate LLM API; the model already running the conversation *is* the rater. The skill is self-contained: it grounds its judgment in `references/principles.json` and `references/non-negotiables.json`, a synced copy of `principles/*.yaml` and `non-negotiables.yaml` generated by `eval/sync_skill_bundle.py` (`make sync-skill-bundle`), and validates against a bundled, dependency-free copy of the CLI (`scripts/assessment.py`, `scripts/principles.py`, `scripts/report.py`) rather than this repo's own `eval/` directly — so the whole skill folder can be handed to someone who doesn't have the rest of this repo. See [Installing this skill elsewhere](#installing-this-skill-elsewhere) below, and that skill's own `SKILL.md` for its five-step procedure and a file-level breakdown of what it reads and calls.

**The validator and renderer — `eval/`.** Once the skill has written an assessment JSON, `eval/assessment.py` (the CLI both the skill and a human can call directly) loads real principle/non-negotiable ids via `eval/principles.py` and checks the JSON against them — a fabricated id, an out-of-range score, or a low score with no mitigation all fail loudly here rather than silently rendering. `eval/report.py` holds the `Assessment`/`PrincipleRating`/`BrightLineFinding` dataclasses and the Markdown renderer, reached only through `assessment.py`. The rendered report lands in `eval/reports/` (gitignored — advisory output, not a build artifact). `eval/` never makes a judgment call itself; it only catches a judgment that doesn't check out.

`docs/` sits outside this runtime path entirely — it's citation research (`ccc-citation-map.md`, `compendium-citation-map.md`, `usccb-foundational-documents-index.md`, `magnifica-humanitas-findings.md`) and process history (`theological-review-log.md`), not something the skill or `eval/` reads at assessment time.

## Stack

Python (`eval/`) for validating and rendering an assessment, following [`docs/standards/python.md`](../docs/standards/python.md) — it never calls an LLM itself; the judgment is made in conversation by whoever runs the `cst-finding` skill, grounded directly in the principle files. YAML for the principle and non-negotiables schema and entries (`principles/`). Markdown for the rubric, tensions library, and integration docs — this repo is a hybrid of code and non-code deliverables, held to both halves of [`docs/standards/architecture.md`](../docs/standards/architecture.md).

## Setup

```
make setup
```

Installs `eval/`'s dependencies (just `pyyaml` plus dev tooling) into a local `.venv`. No API key needed — see Stack above.

## Testing

`make test` runs `eval/`'s test suite against real principle content loaded from `tests/` fixtures built inline, not a mocked target. Once `principles/` and `rubric/` are also reviewed content rather than beta drafts, this project is held to [`CHECKLIST.md`](CHECKLIST.md), which extends the repo's standard [`docs/project-template/CHECKLIST.md`](../docs/project-template/CHECKLIST.md) with this project's own go-live conditions.

### Running an assessment

The normal path is the `cst-finding` Claude Skill (`.claude/skills/cst-finding/`) — it either interviews you about a planned AI use, or takes an actual prompt/response pair to audit, does the rating itself in conversation grounded in `principles/*.yaml`, and calls the CLI below to validate and render the result. To run the CLI directly against an already-written assessment JSON (see `.claude/skills/cst-finding/references/assessment-schema.md` for the shape):

```
.venv/bin/python -m eval.assessment \
  --input path/to/assessment.json \
  --principles-dir principles \
  --out-dir eval/reports
```

`eval/assessment.py` never makes the judgment call — it validates that every principle or non-negotiable id referenced is real, every score is 1-5, and every score of 3 or below carries a mitigation, then renders a timestamped Markdown report. A non-zero exit means the input didn't check out, not that the subject scored badly.

## Security & privacy notes

This project's outputs are advisory findings about *a described AI use or an audited interaction*, not records about real people. When describing a use case, describe it generically — what the system does and decides — rather than pasting in a real person's file, application, or other personal data. When auditing an actual prompt/response pair, the exact text is needed for the rubric to mean anything, but redact or generalize any real person's personal details (names, contact info, case specifics) out of the prompt and response before handing them to the skill; `eval/reports/` should never contain real personal data, per [`docs/standards/security-and-privacy.md`](../docs/standards/security-and-privacy.md). If a dry run against a real institution's use case (see Next Actions in the project log) needs to reference real records to be meaningful, that data stays out of this repository entirely; only de-identified findings are recorded.

## Skills used or provided

- `.claude/skills/cst-finding` (project-local, not shared) — either interviews the user about a planned AI use, or takes an actual prompt/response pair to audit, and rates it against CST, checking `non-negotiables.yaml` first. Lives under `.claude/skills/` rather than the repo's shared `skills/` convention so Claude Code actually discovers and can invoke it in this project — kept project-local because the judgment it's grounded in (`principles/`, `rubric/`) is authored and reviewed as part of this project. It's independently installable elsewhere anyway, because the skill folder bundles its own synced copy of that grounding content — see below.

## Installing this skill elsewhere

The skill folder itself (`.claude/skills/cst-finding/`) is self-contained — it never reaches outside itself for grounding content or for the validator it calls — so it can be installed on its own, without the rest of this repository:

- **Working in this repo already:** nothing to install; Claude Code discovers it under `.claude/skills/` automatically. If you're editing `principles/`, `rubric/`, or `eval/assessment.py`/`eval/report.py`, run `make sync-skill-bundle` afterward — the skill reads its own bundled copy, not those files directly, and `make test` fails if the two drift apart.
- **Claude Code, from this repo as a plugin marketplace:**
  ```
  /plugin marketplace add sgmuff/catholic-ai
  /plugin install cst-finding
  ```
- **Claude.ai (web or desktop):** download the `cst-finding-skill.zip` asset from this repo's [Releases](https://github.com/sgmuff/catholic-ai/releases) page (built by `.github/workflows/release-cst-finding-skill.yml` from the skill folder alone), then in Settings → Capabilities → Skills → Create skill, upload it. Requires "Code execution and file creation" turned on, since step 4 of the skill runs a bundled Python script to validate and render the report.

## Repo structure

```
cst-finding/
├── README.md                    # this file
├── CONTRIBUTING.md              # review process for principles/rubric vs. eval/integrations
├── CODEOWNERS                   # technical maintainer for all of the above
├── CHANGELOG.md                 # versioned against magisterial developments, not sprints
├── CHECKLIST.md                 # this project's go-live checklist, extending the repo default
├── Makefile                     # setup, test, lint
├── pyproject.toml                # eval/'s dependencies (pyyaml + dev tooling only)
├── principles/
│   ├── schema.yaml               # shape every graded principle file follows
│   ├── personalism.yaml
│   ├── common-good.yaml
│   ├── subsidiarity.yaml
│   ├── solidarity.yaml
│   ├── universal-destination-of-goods.yaml
│   ├── preferential-option-for-the-poor.yaml
│   ├── dignity-and-inviolability-of-life.yaml
│   ├── social-justice.yaml       # eighth principle, added from Magnifica Humanitas §77-81
│   └── non-negotiables.yaml      # bright-line gate, checked before the 8 are scored
├── rubric/
│   ├── criteria.md              # the two-stage rubric this project follows; eval/assessment.py validates the shape of it, doesn't implement the judgment
│   └── known-tensions.md        # stress-test library, documented not hidden
├── eval/
│   ├── principles.py             # loads + validates principles/*.yaml and non-negotiables.yaml
│   ├── assessment.py             # validates a written assessment, CLI entry point
│   ├── report.py                 # Assessment/rating dataclasses, markdown rendering + writing
│   ├── sync_skill_bundle.py      # regenerates .claude/skills/cst-finding/{references,scripts}/ — `make sync-skill-bundle`
│   └── reports/                  # advisory output, not a gate — gitignored contents
├── integrations/                 # both files below are TODO stubs, not yet written
│   ├── gateway-hook.md           # will document importing principles/schema.yaml into ai-acceptable-use-gateway
│   └── governance-hook.md        # will document routing a contested case to governance-as-code's required-reviewer mechanism
├── docs/
│   ├── theological-review-log.md
│   ├── compendium-citation-map.md          # source -> principle map, paragraph numbers verified
│   ├── magnifica-humanitas-findings.md     # MH-specific findings, incl. the social-justice addition
│   ├── ccc-citation-map.md                 # Catechism + USCCB-list encyclical citations landed so far
│   └── usccb-foundational-documents-index.md # full USCCB list, what's cited vs. still Tier C
├── .claude/
│   └── skills/
│       └── cst-finding/  # project-local, self-contained Claude Skill: interview + rate
│           ├── SKILL.md
│           ├── .claude-plugin/
│           │   └── plugin.json       # makes this folder installable as a Claude Code plugin
│           ├── references/
│           │   ├── assessment-schema.md
│           │   ├── principles.json   # synced from principles/*.yaml — generated, see eval/sync_skill_bundle.py
│           │   ├── non-negotiables.json  # synced from principles/non-negotiables.yaml — generated
│           │   └── rubric/
│           │       ├── criteria.md       # synced copy of rubric/criteria.md — generated
│           │       └── known-tensions.md # synced copy of rubric/known-tensions.md — generated
│           └── scripts/
│               ├── assessment.py     # portable CLI, stdlib-only — generated from eval/assessment.py
│               ├── principles.py     # portable JSON loader, stdlib-only — generated
│               └── report.py         # verbatim copy of eval/report.py — generated
└── tests/
    ├── test_principles.py
    ├── test_assessment.py
    ├── test_report.py
    └── test_skill_bundle_sync.py  # fails if the bundle above drifts from principles/, rubric/, eval/
```

## Definition of done (v0.1)

- [ ] Eight principle files, fully cited against MH and the Compendium/encyclical sources in each principle's `magisterial_citations`
- [ ] `principles/non-negotiables.yaml` reviewed and confirmed as the complete, correctly-scoped bright-line list
- [ ] A known-tensions library with at least three worked hard cases
- [ ] `eval/assessment.py` and the `cst-finding` skill run against at least one real described use, and at least one real audited prompt/response pair, and produce a report artifact for each
- [ ] Every generated report recommends parish-level pastoral/theological review, and at least one substantive `principles/`/`rubric/` change is logged in `docs/theological-review-log.md`
- [ ] A dry run against 2–3 real use cases with results good enough to present publicly

The principle and non-negotiables content is drafted and the assessment tool runs — but nothing above is checked yet, because nothing has had theological review.
