"""The one metric a generic fairness toolkit doesn't produce: an
asymmetrically-weighted harm score. `metrics.py`'s false-negative and
false-positive rates treat an error against either group as equally
costly — that symmetry is a choice, not a law of nature, and the
preferential option for the poor is a specific claim that it's the wrong
one here. A wrongful denial to the vulnerable group costs more than a
wrongful denial elsewhere; a wrongful approval in the vulnerable group's
favor costs less than a wrongful approval elsewhere. The default weights
below encode that claim as a number so it can be inspected and argued
with, not smuggled in as an unstated assumption.
"""

from __future__ import annotations

from dataclasses import dataclass

from preferential_impact_audit.metrics import Row


@dataclass(frozen=True)
class WeightConfig:
    fn_weight_vulnerable: float = 3.0
    fp_weight_vulnerable: float = 0.5
    fn_weight_other: float = 1.0
    fp_weight_other: float = 1.0


def weighted_harm_score(rows: tuple[Row, ...], weights: WeightConfig) -> float:
    """Sums each row's weighted error cost — 0 for a correct prediction,
    the group-and-direction-appropriate weight for a false negative or
    false positive. Raises ValueError if any row lacks ground truth
    (`actual_positive is None`) rather than silently skipping it: a
    weighted score computed over an incomplete set of outcomes would look
    precise while being wrong."""
    total = 0.0
    for i, row in enumerate(rows):
        if row.actual_positive is None:
            raise ValueError(f"row {i}: missing ground truth ('actual_positive'); cannot weight it")
        if row.actual_positive and not row.predicted_positive:
            total += weights.fn_weight_vulnerable if row.vulnerable else weights.fn_weight_other
        elif not row.actual_positive and row.predicted_positive:
            total += weights.fp_weight_vulnerable if row.vulnerable else weights.fp_weight_other
    return total
