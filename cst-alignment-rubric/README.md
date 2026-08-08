# CST Alignment Rubric

A schema, a graded rubric, and an advisory eval harness that let a team run an AI system against Catholic Social Teaching before it ships — the translation layer CST has never had, the way GDPR Art. 35 turned "protect fundamental rights" into a mandatory, auditable DPIA.

It started life as `cst-model-constitution`. The rename matters and stays visible here: "constitution" implied this shapes model *behavior* the way training-time alignment does. Almost no institution using this repo trains foundation models; they call a vendor API. What this repo does is *audit and advise*, not train. Overclaiming that distinction is how a governance tool turns into ethics-washing — which is exactly what the section below exists to prevent.

## Non-Goals

- **Not a substitute for training-time alignment.** It does not shape model weights. It evaluates the behavior of systems already built or bought.
- **Not a hard CI gate by default.** LLM output is nondeterministic and LLM-as-judge scoring is unreliable on value-laden criteria — a hard block produces flaky builds and false confidence. Default behavior is advisory: flag, route to human review, log.
- **Not a canonical magisterial interpretation.** Competent theologians disagree on contested applications (immigration enforcement and solidarity, labor structures and subsidiarity). The rubric documents a working interpretation, dated and versioned, not "the" Catholic position.
- **Not a certification or marketing claim.** "Passed the rubric" is not a compliance stamp. CI output is worded as advisory, not pass/fail, to make misuse harder.
- **Not a replacement for pastoral or human judgment.** `rubric/known-tensions.md` exists precisely to keep this limitation visible rather than buried.

## Audience

Any institution — Catholic or secular — that has to decide whether an AI system it's about to deploy or has already deployed holds up against Catholic Social Teaching: a diocese or Catholic hospital reviewing a vendor tool, or a secular compliance officer or board who wants the reasoning behind CST's conclusions without first being persuaded of the theology. One rubric, one voice, for both — see [`../CONTRIBUTING.md`](../CONTRIBUTING.md) for why this repository doesn't split confessional and secular readers into separate tracks.

## Status

`draft` (beta). All eight principles and the non-negotiables bright-line list are drafted and cited, and the assessment tool (`eval/assessment.py` + the `rate-ai-against-cst` skill) runs end to end — but every word of principle content is **unreviewed**: no theological reviewer has signed off yet. See [Definition of done (v0.1)](#definition-of-done-v01) for what "active" requires.

The theological-reviewer sign-off requirement in `CODEOWNERS` is paused for this beta phase (see `CONTRIBUTING.md` "Beta status") and will be reimposed, with retroactive review of anything written in the meantime, before this project leaves beta. Any principle or rubric content written during this period is unreviewed and must say so.

## Grounding

Eight principles, each cited directly against *Magnifica Humanitas* paragraph numbers and the wider CST tradition: personalism, common good, subsidiarity, solidarity, universal destination of goods, preferential option for the poor, dignity and inviolability of life, and social justice (added after *Magnifica Humanitas* named it as one of its own headline principles — see `docs/magnifica-humanitas-findings.md`). Where relevant, a principle's rubric criteria are also mapped to NIST AI RMF, ISO/IEC 42001, and the EU AI Act's risk tiers, per [`docs/standards/architecture.md`](../docs/standards/architecture.md#reference-frameworks) — but CST is the throughline those frameworks are judged against, not a parallel authority alongside it.

## How it works, in plain terms

1. **Write down the values.** Each of the eight principles gets its own file: what it means in plain terms, where it comes from in Church teaching, and which other principles it tends to clash with. A separate, smaller file — `principles/non-negotiables.yaml` — holds the handful of things CST treats as settled, not as one factor to weigh: direct abortion, euthanasia, and direct killing of the innocent.
2. **Bring a subject, in conversation.** The `rate-ai-against-cst` Claude Skill takes either of two things: someone deciding whether to build, buy, or keep running a specific AI use describes it — what it does, who it affects, what it decides — with follow-up questions only where the description is genuinely unclear; or someone with an actual prompt and response from a deployed AI system pastes them in verbatim to have that specific interaction audited after the fact.
3. **Check the bright line first.** Before anything gets scored, the subject — the described use, or what the response actually said or did — is checked against `principles/non-negotiables.yaml`. If it matches, the assessment says so plainly and stops there — see [Non-Goals](#non-goals) and `rubric/criteria.md`.
4. **Otherwise, score all eight principles.** Each principle gets a 1-5 score grounded in that principle's own description, a real rationale, and — for anything scoring 3 or below — a specific mitigation, not generic advice. A case where two good principles genuinely disagree gets flagged `contested`, not averaged into a single number.
5. **Hand back a report, not a verdict.** Nothing here is a certification. A low score or even a bright-line match is a finding for a person to act on.
6. **Keep a real person accountable for the definitions.** Changing what a principle or non-negotiable file says requires sign-off from a named theologian, the same way changing a contract needs a lawyer's, not just an engineer's opinion.

## Stack

Python (`eval/`) for validating and rendering an assessment, following [`docs/standards/python.md`](../docs/standards/python.md) — it never calls an LLM itself; the judgment is made in conversation by whoever runs the `rate-ai-against-cst` skill, grounded directly in the principle files. YAML for the principle and non-negotiables schema and entries (`principles/`). Markdown for the rubric, tensions library, and integration docs — this repo is a hybrid of code and non-code deliverables, held to both halves of [`docs/standards/architecture.md`](../docs/standards/architecture.md).

## Setup

```
make setup
```

Installs `eval/`'s dependencies (just `pyyaml` plus dev tooling) into a local `.venv`. No API key needed — see Stack above.

## Testing

`make test` runs `eval/`'s test suite against real principle content loaded from `tests/` fixtures built inline, not a mocked target. Once `principles/` and `rubric/` are also reviewed content rather than beta drafts, this project is held to [`CHECKLIST.md`](CHECKLIST.md), which extends the repo's standard [`docs/project-template/CHECKLIST.md`](../docs/project-template/CHECKLIST.md) with this project's own go-live conditions.

### Running an assessment

The normal path is the `rate-ai-against-cst` Claude Skill (`.claude/skills/rate-ai-against-cst/`) — it either interviews you about a planned AI use, or takes an actual prompt/response pair to audit, does the rating itself in conversation grounded in `principles/*.yaml`, and calls the CLI below to validate and render the result. To run the CLI directly against an already-written assessment JSON (see `.claude/skills/rate-ai-against-cst/references/assessment-schema.md` for the shape):

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

- `.claude/skills/rate-ai-against-cst` (project-local, not shared) — either interviews the user about a planned AI use, or takes an actual prompt/response pair to audit, and rates it against CST, checking `principles/non-negotiables.yaml` first. Lives under `.claude/skills/` rather than the repo's shared `skills/` convention so Claude Code actually discovers and can invoke it in this project — kept project-local because it's tightly coupled to this project's own principle files and file layout, not a capability another project could reuse as-is.

## Repo structure

```
cst-alignment-rubric/
├── README.md                    # this file
├── CONTRIBUTING.md              # theological + technical review process
├── CODEOWNERS                   # named theological reviewer + technical maintainer
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
│   ├── criteria.md              # the two-stage rubric eval/assessment.py implements
│   └── known-tensions.md        # stress-test library, documented not hidden
├── eval/
│   ├── principles.py             # loads + validates principles/*.yaml and non-negotiables.yaml
│   ├── assessment.py             # validates a written assessment, CLI entry point
│   ├── report.py                 # Assessment/rating dataclasses, markdown rendering + writing
│   └── reports/                  # advisory output, not a gate — gitignored contents
├── integrations/
│   ├── gateway-hook.md
│   └── governance-hook.md
├── docs/
│   ├── theological-review-log.md
│   ├── compendium-citation-map.md          # source -> principle map, paragraph numbers verified
│   └── magnifica-humanitas-findings.md     # MH-specific findings, incl. the social-justice addition
├── .claude/
│   └── skills/
│       └── rate-ai-against-cst/  # project-local Claude Skill: interview + rate
│           ├── SKILL.md
│           └── references/
│               └── assessment-schema.md
└── tests/
    ├── test_principles.py
    ├── test_assessment.py
    └── test_report.py
```

## Definition of done (v0.1)

- [ ] Eight principle files, fully cited against MH and the Compendium/encyclical sources in each principle's `magisterial_citations`
- [ ] `principles/non-negotiables.yaml` reviewed and confirmed as the complete, correctly-scoped bright-line list
- [ ] A known-tensions library with at least three worked hard cases
- [ ] `eval/assessment.py` and the `rate-ai-against-cst` skill run against at least one real described use, and at least one real audited prompt/response pair, and produce a report artifact for each
- [ ] A named theological reviewer listed in `CODEOWNERS` with at least one completed review logged in `docs/theological-review-log.md`
- [ ] A dry run against 2–3 real use cases with results good enough to present publicly

The principle and non-negotiables content is drafted and the assessment tool runs — but nothing above is checked yet, because nothing has had theological review.
