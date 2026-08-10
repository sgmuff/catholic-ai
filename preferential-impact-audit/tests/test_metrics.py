import pytest

from preferential_impact_audit.metrics import Row, adverse_impact_ratio, compute_group_metrics

# Hand-computable fixture: 4 vulnerable rows, 4 other rows.
# Vulnerable: 1 TP, 1 FN, 2 TN -> selection rate 1/4, FNR 1/2, FPR 0/2
# Other:      2 TP, 1 FP, 1 TN -> selection rate 3/4, FNR 0/2, FPR 1/2
_ROWS = (
    Row(vulnerable=True, predicted_positive=True, actual_positive=True),
    Row(vulnerable=True, predicted_positive=False, actual_positive=True),
    Row(vulnerable=True, predicted_positive=False, actual_positive=False),
    Row(vulnerable=True, predicted_positive=False, actual_positive=False),
    Row(vulnerable=False, predicted_positive=True, actual_positive=True),
    Row(vulnerable=False, predicted_positive=True, actual_positive=True),
    Row(vulnerable=False, predicted_positive=True, actual_positive=False),
    Row(vulnerable=False, predicted_positive=False, actual_positive=False),
)


def test_compute_group_metrics_selection_rates():
    vulnerable, other = compute_group_metrics(_ROWS)

    assert vulnerable.group == "vulnerable"
    assert vulnerable.n == 4
    assert vulnerable.selection_rate == pytest.approx(0.25)
    assert other.selection_rate == pytest.approx(0.75)


def test_compute_group_metrics_error_rates():
    vulnerable, other = compute_group_metrics(_ROWS)

    assert vulnerable.false_negative_rate == pytest.approx(0.5)
    assert vulnerable.false_positive_rate == pytest.approx(0.0)
    assert other.false_negative_rate == pytest.approx(0.0)
    assert other.false_positive_rate == pytest.approx(0.5)


def test_compute_group_metrics_error_rates_none_without_labels():
    unlabeled = tuple(
        Row(vulnerable=r.vulnerable, predicted_positive=r.predicted_positive, actual_positive=None)
        for r in _ROWS
    )

    vulnerable, other = compute_group_metrics(unlabeled)

    assert vulnerable.false_negative_rate is None
    assert vulnerable.false_positive_rate is None
    assert other.false_negative_rate is None
    assert other.false_positive_rate is None


def test_compute_group_metrics_raises_when_a_group_is_empty():
    only_vulnerable = tuple(r for r in _ROWS if r.vulnerable)

    with pytest.raises(ValueError, match="non-vulnerable"):
        compute_group_metrics(only_vulnerable)


def test_adverse_impact_ratio():
    vulnerable, other = compute_group_metrics(_ROWS)

    ratio = adverse_impact_ratio(vulnerable, other)

    assert ratio == pytest.approx(0.25 / 0.75)


def test_adverse_impact_ratio_raises_when_other_selection_rate_is_zero():
    vulnerable, other = compute_group_metrics(_ROWS)
    zero_rate_other = other.__class__(
        group="other",
        n=other.n,
        selection_rate=0.0,
        false_negative_rate=None,
        false_positive_rate=None,
    )

    with pytest.raises(ValueError, match="selection rate is 0"):
        adverse_impact_ratio(vulnerable, zero_rate_other)
