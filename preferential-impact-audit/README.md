# Preferential-impact audit

Computes standard fairness/disparate-impact metrics over a dataset of automated decisions, plus one metric a generic fairness toolkit doesn't produce: an asymmetrically-weighted harm score that costs a wrongful denial to an economically vulnerable group more than a symmetric parity metric would.

## Non-Goals

- **Not a substitute for a full legal fair-lending or EEOC compliance review.** This measures disparity; it doesn't certify compliance.
- **Doesn't explain the disparity.** A flagged result says outcomes differ between groups — it says nothing about whether that's bias in the model, in the training data, or in the underlying process being modeled.
- **Never approximates the weighted score without ground truth.** The weighted-harm metric requires knowing actual outcomes, not just predictions. When a `label_column` isn't given, the report says the score was skipped, rather than guessing at it from selection rates alone.

## Audience

Any organization deploying automated decisioning over consequential access to credit, employment, housing, or benefits — general enterprise ML, not limited to any particular kind of institution.

## Status

`draft`. Runs end to end against fixtures (`make setup lint test`), including both with and without ground-truth labels. The default weights (below) are a first draft and haven't been reviewed by anyone with expertise in fair-lending law or algorithmic-fairness practice.

## Grounding

Standard fairness metrics — selection-rate parity, equalized odds — treat every subgroup's errors as equally weighted: a false denial to one group and a false denial to another count the same in the arithmetic. The preferential option for the poor is a specific claim that they shouldn't: a wrongful denial to someone already economically vulnerable is a graver harm than the same error elsewhere, and a wrongful approval in their favor is a lesser one. This project doesn't replace the standard metrics with that claim — it computes both, side by side, so the difference the weighting makes is visible rather than asserted as the only correct reading.

A reader who doesn't share the theology can still act on the result directly: the default weights (false-negative to the vulnerable group weighted 3×, false-positive to the vulnerable group weighted 0.5×, both symmetric elsewhere) are stated plainly and are fully overridable at the command line — nothing here is hidden inside the arithmetic. The standard metrics are anchored to the EEOC's four-fifths rule (a selection-rate ratio below 0.8 is the recognized threshold for flagging adverse impact) and the EU AI Act's Annex III high-risk categories, which include credit, employment, and essential-services decisioning.

## Stack

Python 3.12, `src/` layout, zero runtime dependencies — dataset loading uses the standard library's `csv` module rather than pandas or numpy, since nothing here needs more than reading a text file and counting.

## Setup

```
make setup
```

Requires Python 3.12+; if your default `python3` resolves to an older interpreter, create the venv with a 3.12 binary directly (e.g. `python3.12 -m venv .venv`) before the rest of `make setup`.

## Testing

```
make test
```

Every metric and weighting function is tested against small, hand-computable fixtures — a handful of rows where the selection rate, error rates, adverse-impact ratio, and weighted score can all be verified by hand and asserted exactly, rather than tested only against opaque real-scale data. `make lint` runs `ruff check`, `ruff format --check`, and `mypy --strict`.

### Running a real audit

```
.venv/bin/python -m preferential_impact_audit.runner \
  --data predictions.csv \
  --protected-column income_bracket \
  --vulnerable-value low \
  --prediction-column approved \
  --positive-value yes \
  --label-column repaid \
  --positive-label-value yes \
  --out-dir reports
```

`--label-column`/`--positive-label-value` are optional together — omit both to get the standard metrics and adverse-impact ratio without the weighted score. Override any default weight with `--fn-weight-vulnerable`, `--fp-weight-vulnerable`, `--fn-weight-other`, `--fp-weight-other`. Inspect the generated report in `reports/` (gitignored) and its running `reports/INDEX.md`.

## Security & privacy notes

The input CSV is a dataset of decisions, not identified individuals as such, but it can still be sensitive — protected-attribute and outcome data about real people. This project never stores or transmits the input file anywhere; it reads it once, computes aggregate group statistics, and writes only those aggregates to the report. No row-level data appears in any generated report. Whoever runs this tool is responsible for the input file's own handling under their organization's data-protection obligations before it ever reaches this tool.

## Skills used or provided

None. Every number in this report is a deterministic computation over the input data — there's no judgment call here for an LLM to make or defer.

## Definition of done (v0.1)

- [x] Standard group metrics (selection rate, FNR, FPR) and the four-fifths adverse-impact ratio implemented and tested against hand-computed fixtures
- [x] Weighted harm score implemented, configurable, and skipped (not approximated) without ground truth
- [x] CLI runs end to end both with and without a label column
- [x] Report renders and writes correctly, `reports/` gitignored
- [ ] Default weights reviewed by someone with fair-lending law or algorithmic-fairness expertise
- [ ] Dry run against a real (or realistic synthetic) dataset with results worth presenting
