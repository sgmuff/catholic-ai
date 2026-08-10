# Guardrail probing

An automated adversarial test harness for LLMs and agentic systems: it runs a corpus of jailbreak, prompt-injection, secrets-exfiltration, doctrinal-reliability, and manipulation-to-harm probes against a real endpoint and reports where its guardrails held or failed.

## Non-Goals

- **Not a safety certification.** A clean run means the target resisted the probes actually in this corpus — nothing more. The report is worded as findings, never as "passed" or "certified safe."
- **Not a substitute for a professional security review or penetration test.** This is a repeatable regression check an institution runs before and after a deployment change, not a one-time audit by security specialists.
- **Not a runtime guardrail.** It's an offline test harness a person or CI runs periodically, not request-time protection.
- **Fully standalone.** This project follows this repo's shared conventions (`docs/standards/`), but is otherwise self-contained — no code, schema, or skill from anywhere else is required to build, run, or understand it.
- **Not an LLM-as-judge tool.** Where a probe's outcome is mechanically checkable (a canary string leaked, a compliance marker present), the harness scores it automatically. Where it isn't (does a response misstate doctrine, does it actually facilitate harm), it captures the response and flags it for a human — see `src/guardrail_probing/detectors.py`.

## Audience

Any institution running its own LLM-backed chatbot or agentic tool against the public or its own staff — a parish or diocesan assistant, a Catholic hospital's or university's internal copilot, a Catholic charity's intake bot. Equally usable by a secular organization running the same kind of system; only the doctrinal-reliability category assumes a Catholic institutional context, and it's one file among five.

## Status

`draft`. The harness runs end to end (`make setup lint test`, 39 tests, 93% coverage) against a stub target, and a documented manual command exists for running it against a real endpoint — but the probe corpus is a first draft (5 probes per category, 25 total) and the doctrinal-reliability probes' factual content has not yet been reviewed by anyone theologically competent. See Definition of done below.

## Grounding

This project asserts no Catholic Social Teaching *judgment* of its own — it doesn't score a use case against CST principles. It tests something narrower and more mechanical: whether a deployed system's guardrails hold under adversarial pressure. Two of its five probe categories are where a Catholic institutional context actually changes what's worth testing for, rather than just relabeling a generic red-team corpus:

- **`doctrinal-reliability`** — does the system assert something false about Church teaching, or claim an authority (sacramental, tribunal) it doesn't have, with unwarranted confidence under leading or adversarial framing. No secular red-team corpus has a reason to include this category.
- **`manipulation-to-harm`** — does a false-authority or fictional framing talk the system into facilitating something Catholic Social Teaching treats as a serious harm — direct abortion, exploitation of the poor, trafficking, and the like: the kind of thing CST treats as a bright line, not one factor among several to weigh.

The other three categories (`jailbreak`, `prompt-injection`, `secrets-exfiltration`) are standard adversarial-testing concerns, authored from scratch here rather than imported from an existing red-team library, so the whole project stays dependency-free and legible.

A reader who doesn't share the theology can use this project exactly as-is: run it, read the findings, decide what to fix. The Catholic grounding shapes which probes exist, not how the harness itself works.

## Stack

Python 3.12, `src/` layout per [`docs/standards/python.md`](../docs/standards/python.md). One runtime dependency: `pyyaml`, for loading `probes/*.yaml`. No LLM API is called by the harness's own logic — only the target under test is called, via plain `urllib` (no HTTP client dependency).

## Setup

```
make setup
```

Installs `pytest`, `pytest-cov`, `ruff`, `mypy`, and `pyyaml` into a local `.venv`. Requires Python 3.12+; if your default `python3` resolves to an older interpreter, point the venv creation at a 3.12 binary directly (e.g. `python3.12 -m venv .venv`) before running the rest of `make setup`.

## Testing

```
make test
```

Runs the full suite against fixtures built inline (`tests/`), never against a real network endpoint or a real LLM — every `Target` used in tests is a small stub or an injected fake HTTP transport, so the suite is deterministic, free, and never flaky from a live model's nondeterminism. `make lint` runs `ruff check`, `ruff format --check`, and `mypy --strict`.

### Running a probe corpus against a real target

Not part of CI — this calls a real endpoint and needs a real API key:

```
export MY_TARGET_API_KEY=...
.venv/bin/python -m guardrail_probing.runner \
  --target-url https://api.example.com/v1 \
  --api-key-env MY_TARGET_API_KEY \
  --model my-model-name \
  --out-dir reports
```

Assumes an OpenAI-compatible `chat/completions` endpoint. Omit `--api-key-env` entirely for a target that doesn't require one (a local model server, an internal endpoint behind network isolation instead of auth) — no `Authorization` header is sent. The `secrets-exfiltration` probes only mean something if the target's own system prompt is configured with the canary token they check for (`GUARDRAIL-CANARY` by default — see `probes/secrets-exfiltration.yaml`); without it, those probes will always "pass" for the wrong reason. Inspect the generated report in `reports/` (gitignored) and its running `reports/INDEX.md`.

### Testing something that isn't an HTTP chat-completions API

`HttpEndpointTarget` is one adapter, not a requirement — `Target` is a `Protocol` with a single `send(turns) -> str` method. To probe a Slack/Teams bot, an agentic framework reached only through its own SDK, or anything else `HttpEndpointTarget` can't reach, write a small class satisfying that protocol and call `run_corpus`/`write_report` directly instead of going through the CLI:

```python
from pathlib import Path
from guardrail_probing.probes import load_probes
from guardrail_probing.runner import run_corpus
from guardrail_probing.report import write_report


class MyTarget:
    def send(self, turns):
        return my_own_integration.ask(turns)  # however you actually reach the system


probes = load_probes(Path("probes"))
findings = run_corpus(probes.values(), MyTarget())
write_report(findings, Path("reports"))
```

## Security & privacy notes

No real personal data appears anywhere in the probe corpus or test fixtures — every probe is a synthetic adversarial prompt, not a record about a real person, so `docs/standards/security-and-privacy.md`'s data-minimization and retention questions don't apply to this project's own inputs. What does apply: the API key for a target under test is passed by environment-variable name only (`--api-key-env`), never as a literal argument or committed anywhere. Generated reports (`reports/`, gitignored except `.gitkeep`) are treated as sensitive — a report proving a real deployed system is jailbreakable is a live vulnerability disclosure, not a build artifact, and shouldn't sit in git history or be shared outside the people responsible for fixing it. Every `needs_review` finding is exactly the human-oversight requirement `security-and-privacy.md` calls for applied to this project's own output: no automated verdict is rendered on doctrinal accuracy or harm-facilitation, and the report says so on every run.

## Skills used or provided

None. This is a CLI tool, not a conversational skill — running it doesn't require an LLM to make a judgment call in conversation; the judgment either resolves mechanically (a detector) or is explicitly deferred to a human (`needs_review`).

## Definition of done (v0.1)

- [x] Probe corpus schema defined and validated (`src/guardrail_probing/probes.py`)
- [x] ~25 probes across the 5 categories
- [x] All deterministic detectors covered by golden-fixture tests; `manual_review` category never auto-scored
- [x] `run_corpus` proven end-to-end against a stub target in tests; a documented manual command exists for a real endpoint
- [x] Report renders and writes correctly, `reports/` gitignored
- [ ] Doctrinal-reliability probes' factual content reviewed by someone theologically competent
- [ ] Corpus dry-run against at least one real deployed system, with results worth presenting
