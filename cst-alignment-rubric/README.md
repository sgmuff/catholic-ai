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

`draft` — scaffolding only. No principle content has been written yet; see [Definition of done (v0.1)](#definition-of-done-v01) for what "active" requires.

## Grounding

Seven principles, each cited directly against *Magnifica Humanitas* paragraph numbers and the wider CST tradition: personalism, common good, subsidiarity, solidarity, universal destination of goods, preferential option for the poor, and the dignity and inviolability of life. Where relevant, a principle's rubric criteria are also mapped to NIST AI RMF, ISO/IEC 42001, and the EU AI Act's risk tiers, per [`docs/standards/architecture.md`](../docs/standards/architecture.md#reference-frameworks) — but CST is the throughline those frameworks are judged against, not a parallel authority alongside it.

## How it works, in plain terms

1. **Write down the values.** Each of the seven principles gets its own file: what it means in plain terms, where it comes from in Church teaching, and which other principles it tends to clash with.
2. **Write down example situations in advance.** For each principle, a few realistic scenarios are written out ahead of time, including at least one genuinely hard case where two good principles disagree.
3. **Run the AI through those scenarios**, before it goes live or on a regular schedule afterward, and record its answers.
4. **Score the answers more than one way.** Several separate reviews rate how well each answer lines up with the principle. Disagreement or genuine ambiguity isn't forced into a grade — it gets flagged "send this to a person."
5. **Hand back a report, not a verdict.** A low score doesn't automatically block anything from shipping — a person makes the call.
6. **Keep a real person accountable for the definitions.** Changing what a principle file says requires sign-off from a named theologian, the same way changing a contract needs a lawyer's, not just an engineer's opinion.

## Stack

Python for the eval harness (`eval/`), following [`docs/standards/python.md`](../docs/standards/python.md). YAML for the principle schema and entries (`principles/`). Markdown for the rubric, tensions library, and integration docs — this repo is a hybrid of code and non-code deliverables, held to both halves of [`docs/standards/architecture.md`](../docs/standards/architecture.md).

## Setup

```
make setup
```

Installs the eval harness's dependencies into a local `.venv`. Nothing else in this project currently requires setup — `principles/` and `rubric/` are plain files.

## Testing

`make test` runs the eval harness's test suite (currently a placeholder — the harness itself isn't implemented yet). Once `principles/`, `rubric/`, and `eval/` have real content, this project is also held to [`CHECKLIST.md`](CHECKLIST.md), which extends the repo's standard [`docs/project-template/CHECKLIST.md`](../docs/project-template/CHECKLIST.md) with this project's own go-live conditions (seven cited principle files, a three-case tensions library, a logged theological review).

## Security & privacy notes

This project's outputs are evaluation reports about *an AI system's behavior on hypothetical scenarios*, not records about real people. `eval/reports/` should never contain output generated against real personal data — scenario prompts are fabricated or drawn from genuinely public sources, per [`docs/standards/security-and-privacy.md`](../docs/standards/security-and-privacy.md). If a dry run against a real institution's use case (see Next Actions in the project log) requires touching real records, that data stays out of this repository entirely; only de-identified findings are recorded.

## Skills used or provided

None yet.

## Repo structure

```
cst-alignment-rubric/
├── README.md                    # this file
├── CONTRIBUTING.md              # theological + technical review process
├── CODEOWNERS                   # named theological reviewer + technical maintainer
├── CHANGELOG.md                 # versioned against magisterial developments, not sprints
├── CHECKLIST.md                 # this project's go-live checklist, extending the repo default
├── Makefile                     # setup, test, lint
├── pyproject.toml                # eval harness dependencies
├── principles/
│   ├── schema.yaml               # shape every principle file follows
│   ├── personalism.yaml
│   ├── common-good.yaml
│   ├── subsidiarity.yaml
│   ├── solidarity.yaml
│   ├── universal-destination-of-goods.yaml
│   ├── preferential-option-for-the-poor.yaml
│   └── dignity-and-inviolability-of-life.yaml
├── rubric/
│   ├── criteria.md              # graded scale + contested-case flag
│   ├── known-tensions.md        # stress-test library, documented not hidden
│   └── scenarios/
├── eval/
│   ├── harness.py
│   ├── raters/                  # multi-rater config
│   └── reports/                 # advisory output, not a gate
├── integrations/
│   ├── ci-advisory-check.yml    # GitHub Actions, non-blocking by default
│   ├── gateway-hook.md
│   └── governance-hook.md
├── docs/
│   └── theological-review-log.md
└── tests/
    └── test_harness.py
```

## Definition of done (v0.1)

- [ ] Seven principle files, fully cited against MH and the Compendium/encyclical sources in each principle's `magisterial_citations`
- [ ] A known-tensions library with at least three worked hard cases
- [ ] A harness that runs locally and in CI as an advisory (non-blocking) check producing a report artifact on a PR
- [ ] A named theological reviewer listed in `CODEOWNERS` with at least one completed review logged in `docs/theological-review-log.md`
- [ ] A dry run against 2–3 real use cases with results good enough to present publicly

None of these are done yet — this is the v0.1 scaffold only.
