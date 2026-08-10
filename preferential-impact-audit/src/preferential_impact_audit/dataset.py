"""Loads a CSV of predictions/labels/protected attribute into `Row`
objects — stdlib `csv`, no pandas/numpy, so this project takes on no
dependency heavier than reading a text file. Ground truth (`actual_positive`)
is optional: many real audits don't have it (a denied loan applicant's
counterfactual repayment is never observed), so `label_column` is the one
argument that's allowed to be entirely absent — but if given, it has to
come with `positive_label_value` naming what counts as a positive outcome
in that column, not one without the other.
"""

from __future__ import annotations

import csv
from pathlib import Path

from preferential_impact_audit.metrics import Row


def load_dataset(
    path: Path,
    protected_column: str,
    vulnerable_value: str,
    prediction_column: str,
    positive_value: str,
    label_column: str | None = None,
    positive_label_value: str | None = None,
) -> tuple[Row, ...]:
    if (label_column is None) != (positive_label_value is None):
        raise ValueError(
            "'label_column' and 'positive_label_value' must be given together, or not at all"
        )

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        required = [protected_column, prediction_column, *([label_column] if label_column else [])]
        missing = [c for c in required if c not in fieldnames]
        if missing:
            raise ValueError(f"{path}: missing required column(s) {missing}; found {fieldnames}")

        rows = []
        for raw in reader:
            rows.append(
                Row(
                    vulnerable=raw[protected_column] == vulnerable_value,
                    predicted_positive=raw[prediction_column] == positive_value,
                    actual_positive=(raw[label_column] == positive_label_value)
                    if label_column
                    else None,
                )
            )

    if not rows:
        raise ValueError(f"{path}: no data rows found")
    return tuple(rows)
