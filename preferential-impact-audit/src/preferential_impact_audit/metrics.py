"""The shape of one scored decision, and the standard group-level fairness
metrics computed over a set of them: selection rate, false negative/positive
rate per group, and the adverse-impact ratio the EEOC's four-fifths rule is
built on (a selection-rate ratio below 0.8 is the recognized threshold for
flagging adverse impact). Every metric here treats both groups symmetrically
— that's the standard practice this project's other module, `weighting.py`,
exists to depart from on purpose.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Row:
    vulnerable: bool
    predicted_positive: bool
    actual_positive: bool | None


@dataclass(frozen=True)
class GroupMetrics:
    group: str
    n: int
    selection_rate: float
    false_negative_rate: float | None
    false_positive_rate: float | None


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _group_metrics(group: str, rows: list[Row]) -> GroupMetrics:
    n = len(rows)
    selected = sum(1 for r in rows if r.predicted_positive)
    selection_rate = selected / n if n else 0.0

    labeled = [r for r in rows if r.actual_positive is not None]
    if labeled:
        actual_positive = [r for r in labeled if r.actual_positive]
        actual_negative = [r for r in labeled if not r.actual_positive]
        false_negatives = sum(1 for r in actual_positive if not r.predicted_positive)
        false_positives = sum(1 for r in actual_negative if r.predicted_positive)
        fnr = _rate(false_negatives, len(actual_positive))
        fpr = _rate(false_positives, len(actual_negative))
    else:
        fnr = None
        fpr = None

    return GroupMetrics(
        group=group,
        n=n,
        selection_rate=selection_rate,
        false_negative_rate=fnr,
        false_positive_rate=fpr,
    )


def compute_group_metrics(rows: tuple[Row, ...]) -> tuple[GroupMetrics, GroupMetrics]:
    """Splits `rows` into the vulnerable and other groups and computes each
    group's metrics independently. Raises ValueError if either group is
    empty — a ratio computed against zero people in a group isn't
    meaningful."""
    vulnerable_rows = [r for r in rows if r.vulnerable]
    other_rows = [r for r in rows if not r.vulnerable]
    if not vulnerable_rows:
        raise ValueError("no rows belong to the vulnerable group")
    if not other_rows:
        raise ValueError("no rows belong to the non-vulnerable group")
    return _group_metrics("vulnerable", vulnerable_rows), _group_metrics("other", other_rows)


def adverse_impact_ratio(vulnerable: GroupMetrics, other: GroupMetrics) -> float:
    """The EEOC four-fifths rule's ratio: the vulnerable group's selection
    rate divided by the more-favored group's. A ratio below 0.8 is the
    recognized threshold for flagging adverse impact."""
    if other.selection_rate == 0:
        raise ValueError(
            "cannot compute adverse impact ratio: the other group's selection rate is 0"
        )
    return vulnerable.selection_rate / other.selection_rate
