# Appeal-path audit

Audits whether an automated-decision system actually implements a functioning human-appeal path — not just claims one on paper. Two independent checks: does the adverse-decision notice disclose what it's legally required to, and does the documented appeal channel actually accept and acknowledge a request.

## Non-Goals

- **Only a self-audit tool.** Run by an organization against its own decisioning system, or one it's contracted to audit. Never usable to test a third party's live production system without authorization — the channel-probe half submits a real request to a real endpoint, and doing that against a system you don't have the right to test isn't something this tool is for.
- **Never verifies genuine reconsideration.** A channel-probe finding only establishes that a request was accepted and a response came back — not that a human actually looked at the case. That deeper claim isn't mechanically verifiable, so every channel probe pairs its reachability finding with a `needs_review` finding carrying the captured response for a person to judge.
- **Not a certification.** A clean run means the specific notices and channels tested checked out — nothing broader, and nothing about notices or channels that weren't tested.

## Audience

Any organization running automated decisioning that produces consequential outcomes for people — lending, hiring, benefits, insurance — whether or not it's Catholic-run. The notice-disclosure rules cite GDPR and EU AI Act obligations that apply the same way to any organization subject to them.

## Status

`draft`. Both halves run end to end against fixtures and stub channels (`make setup lint test`, 41 tests, 97% coverage); the rule corpus is a first draft (7 rules across two frameworks) and hasn't been checked by anyone with legal expertise in either framework.

## Grounding

The premise here is a specific claim: an automated decision that displaces human judgment still owes the person it affects a real path back to a human, not just a documented one. A notice that never mentions automation, or an appeal address that silently drops every request, makes that path fictional regardless of what a policy document says. This project tests for the fiction, not just the policy.

Two recognized frameworks anchor the notice-disclosure rules: GDPR Art. 22(3), which requires disclosure of automated processing and the right to human intervention for decisions with legal or similarly significant effects, and the EU AI Act's human-oversight obligations for high-risk systems (credit, employment, and similar consequential decisions fall under its Annex III). A reader who doesn't share the theology behind why this matters can still act on it directly: these are binding requirements in the jurisdictions that impose them, tested here as an actual check rather than a checkbox.

## Stack

Python 3.12, `src/` layout. One runtime dependency: `pyyaml`, for loading `rules/*.yaml` and channel configs. No LLM is called anywhere in this project — every check here is either a text-pattern match or an HTTP status check.

## Setup

```
make setup
```

Requires Python 3.12+; if your default `python3` resolves to an older interpreter, create the venv with a 3.12 binary directly (e.g. `python3.12 -m venv .venv`) before the rest of `make setup`.

## Testing

```
make test
```

No test ever makes a real network call — the channel adapter takes an injectable transport, faked in every test, the same way loader tests build fixtures inline under `tmp_path` rather than reading real files from disk. `make lint` runs `ruff check`, `ruff format --check`, and `mypy --strict`.

### Running a real audit

Auditing your own notice templates (no network call, safe to run anytime):

```
.venv/bin/python -m appeal_path_audit.runner audit-notices \
  --notices-dir notices/ \
  --rules-dir rules/ \
  --out-dir reports
```

`notices/` holds your own adverse-decision notice text files (one `.txt` file per notice type). Not part of this repository — these are your organization's actual artifacts.

Probing a real appeal channel — **only run this against a channel you own or are authorized to test**:

```
.venv/bin/python -m appeal_path_audit.runner probe-channel \
  --channel-config channel.yaml \
  --out-dir reports
```

`channel.yaml` describes the test request:

```yaml
id: loan-appeal-channel
url: https://your-own-system.example.com/api/appeals
payload:
  applicant_id: "TEST-0001"
  reason: "requesting human review of automated decision"
expected_status_min: 200
expected_status_max: 299
confirmation_marker: "ticket_id"
```

Inspect the generated report in `reports/` (gitignored) and its running `reports/INDEX.md`.

## Security & privacy notes

Channel-probe payloads must be synthetic test data — a fabricated applicant id, never a real person's application or personal information. Notice files being audited are an organization's own template text, not records about a specific person, so no real personal data should ever need to appear in either input. Generated reports (`reports/`, gitignored except `.gitkeep`) can contain a live system's actual response body, so they're treated as internal artifacts, not committed. Every `needs_review` finding is a deliberate refusal to render an automated verdict on whether a human genuinely reconsidered a case — that judgment stays with a person, on purpose, every time.

## Skills used or provided

None. Every check here is deterministic — a text pattern or an HTTP status — except the one question this project explicitly refuses to automate (whether a response shows genuine human reconsideration), which stays a `needs_review` finding rather than being handed to an LLM to guess at.

## Definition of done (v0.1)

- [x] Rule corpus schema defined and validated (`src/appeal_path_audit/rules.py`)
- [x] 7 rules across two frameworks (GDPR Art. 22, EU AI Act human oversight)
- [x] Both subcommands (`audit-notices`, `probe-channel`) proven end-to-end against fixtures and a stub channel
- [x] Report renders and writes correctly, `reports/` gitignored
- [ ] Rule corpus reviewed by someone with legal expertise in GDPR and the EU AI Act
- [ ] Dry run against at least one real organization's real notices and appeal channel, with results worth presenting
