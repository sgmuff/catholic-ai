"""CLI: load a dataset, compute the standard group metrics and the
four-fifths adverse-impact ratio always, compute the weighted harm score
only when ground-truth labels were given, and write a report. Validates
everything up front, exits 1 with a clear message on anything that doesn't
check out, never partially writes a report.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from preferential_impact_audit.dataset import load_dataset
from preferential_impact_audit.metrics import adverse_impact_ratio, compute_group_metrics
from preferential_impact_audit.report import AuditReport, now_utc, write_report
from preferential_impact_audit.weighting import WeightConfig, weighted_harm_score


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--protected-column", required=True)
    parser.add_argument("--vulnerable-value", required=True)
    parser.add_argument("--prediction-column", required=True)
    parser.add_argument("--positive-value", required=True)
    parser.add_argument(
        "--label-column", default=None, help="Optional; enables the weighted harm score"
    )
    parser.add_argument("--positive-label-value", default=None)
    parser.add_argument(
        "--fn-weight-vulnerable", type=float, default=WeightConfig().fn_weight_vulnerable
    )
    parser.add_argument(
        "--fp-weight-vulnerable", type=float, default=WeightConfig().fp_weight_vulnerable
    )
    parser.add_argument("--fn-weight-other", type=float, default=WeightConfig().fn_weight_other)
    parser.add_argument("--fp-weight-other", type=float, default=WeightConfig().fp_weight_other)
    parser.add_argument("--out-dir", type=Path, default=Path("reports"))
    args = parser.parse_args(argv)

    try:
        rows = load_dataset(
            args.data,
            protected_column=args.protected_column,
            vulnerable_value=args.vulnerable_value,
            prediction_column=args.prediction_column,
            positive_value=args.positive_value,
            label_column=args.label_column,
            positive_label_value=args.positive_label_value,
        )
        vulnerable, other = compute_group_metrics(rows)
        ratio = adverse_impact_ratio(vulnerable, other)
    except ValueError as exc:
        print(f"Could not compute metrics: {exc}", file=sys.stderr)
        return 1

    weights: WeightConfig | None = None
    weighted_harm: float | None = None
    if args.label_column:
        weights = WeightConfig(
            fn_weight_vulnerable=args.fn_weight_vulnerable,
            fp_weight_vulnerable=args.fp_weight_vulnerable,
            fn_weight_other=args.fn_weight_other,
            fp_weight_other=args.fp_weight_other,
        )
        try:
            weighted_harm = weighted_harm_score(rows, weights)
        except ValueError as exc:
            print(f"Could not compute weighted harm score: {exc}", file=sys.stderr)
            return 1

    report = AuditReport(
        generated_at=now_utc(),
        vulnerable=vulnerable,
        other=other,
        adverse_impact_ratio=ratio,
        weighted_harm=weighted_harm,
        weights=weights,
    )
    path = write_report(report, args.out_dir)
    print(f"Report written to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
