"""The shape of an audit run's results, and how they're rendered and
written. Always includes the standard, symmetric metrics; includes the
weighted-harm score only when ground truth was available, placed directly
next to the standard numbers so a reader sees exactly what the weighting
changed rather than being asked to take it on faith.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from preferential_impact_audit.metrics import GroupMetrics
from preferential_impact_audit.weighting import WeightConfig

_DISCLAIMER = (
    "This report measures disparity in outcomes between groups — it does not establish why a "
    "disparity exists (bias in the model, in the data, or in the underlying process), and it is "
    "not a substitute for a full legal fair-lending or EEOC compliance review."
)

_FOUR_FIFTHS_THRESHOLD = 0.8


@dataclass(frozen=True)
class AuditReport:
    generated_at: datetime
    vulnerable: GroupMetrics
    other: GroupMetrics
    adverse_impact_ratio: float
    weighted_harm: float | None
    weights: WeightConfig | None


def _rate_str(value: float | None) -> str:
    return f"{value:.1%}" if value is not None else "n/a (no ground truth)"


def render_markdown(report: AuditReport) -> str:
    flagged = report.adverse_impact_ratio < _FOUR_FIFTHS_THRESHOLD
    lines = [
        "# Preferential-impact audit report",
        "",
        _DISCLAIMER,
        "",
        f"- Generated: {report.generated_at.isoformat()}",
        f"- Vulnerable group size: {report.vulnerable.n}",
        f"- Other group size: {report.other.n}",
        "",
        "## Standard metrics",
        "",
        "| Group | Selection rate | False negative rate | False positive rate |",
        "| --- | --- | --- | --- |",
        (
            f"| Vulnerable | {report.vulnerable.selection_rate:.1%} | "
            f"{_rate_str(report.vulnerable.false_negative_rate)} | "
            f"{_rate_str(report.vulnerable.false_positive_rate)} |"
        ),
        (
            f"| Other | {report.other.selection_rate:.1%} | "
            f"{_rate_str(report.other.false_negative_rate)} | "
            f"{_rate_str(report.other.false_positive_rate)} |"
        ),
        "",
        "## Four-fifths rule (EEOC adverse-impact ratio)",
        "",
        (
            f"Ratio: {report.adverse_impact_ratio:.3f} "
            f"({'below' if flagged else 'at or above'} the {_FOUR_FIFTHS_THRESHOLD} threshold)."
        ),
        "",
        "**Adverse impact flagged.**" if flagged else "**No adverse impact flagged by this rule.**",
        "",
    ]

    if report.weighted_harm is not None and report.weights is not None:
        lines.extend(
            [
                "## Weighted harm score",
                "",
                (
                    "Unlike the symmetric metrics above, this score costs a wrongful denial to "
                    "the vulnerable group more than one elsewhere, and a wrongful approval in "
                    "the vulnerable group's favor less — the preferential option for the poor "
                    "stated as a number, not a relabeling of the standard metrics."
                ),
                "",
                f"- Weighted harm score: {report.weighted_harm:.2f}",
                (
                    f"- Weights used: false-negative (vulnerable) "
                    f"×{report.weights.fn_weight_vulnerable}, "
                    f"false-positive (vulnerable) ×{report.weights.fp_weight_vulnerable}, "
                    f"false-negative (other) ×{report.weights.fn_weight_other}, "
                    f"false-positive (other) ×{report.weights.fp_weight_other}"
                ),
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Weighted harm score",
                "",
                (
                    "Skipped — no ground-truth label column was given. This score is never "
                    "approximated without it."
                ),
                "",
            ]
        )

    return "\n".join(lines)


_INDEX_HEADER = (
    "# Preferential-impact audit run index\n\n"
    "Every report generated in this directory, oldest first.\n\n"
    "| Date | Adverse impact ratio | Flagged | Weighted harm | Report |\n"
    "| --- | --- | --- | --- | --- |\n"
)


def _update_index(out_dir: Path, report: AuditReport, report_path: Path) -> None:
    index_path = out_dir / "INDEX.md"
    if not index_path.exists():
        index_path.write_text(_INDEX_HEADER)
    flagged = "yes" if report.adverse_impact_ratio < _FOUR_FIFTHS_THRESHOLD else "no"
    weighted = f"{report.weighted_harm:.2f}" if report.weighted_harm is not None else "n/a"
    date = report.generated_at.strftime("%Y-%m-%d")
    row = (
        f"| {date} | {report.adverse_impact_ratio:.3f} | {flagged} | {weighted} | "
        f"[{report_path.name}]({report_path.name}) |\n"
    )
    with index_path.open("a") as f:
        f.write(row)


def write_report(report: AuditReport, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    date = report.generated_at.strftime("%Y-%m-%d-%H%M%S")
    path = out_dir / f"{date}-run.md"
    suffix = 2
    while path.exists():
        path = out_dir / f"{date}-run-{suffix}.md"
        suffix += 1
    path.write_text(render_markdown(report))
    _update_index(out_dir, report, path)
    return path


def now_utc() -> datetime:
    return datetime.now(UTC)
