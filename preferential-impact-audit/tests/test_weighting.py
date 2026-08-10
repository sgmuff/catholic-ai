import pytest

from preferential_impact_audit.metrics import Row
from preferential_impact_audit.weighting import WeightConfig, weighted_harm_score

# Same fixture as test_metrics.py: vulnerable has 1 FN, 0 FP; other has 0 FN, 1 FP.
_ROWS = (
    Row(vulnerable=True, predicted_positive=True, actual_positive=True),
    Row(vulnerable=True, predicted_positive=False, actual_positive=True),  # vulnerable FN
    Row(vulnerable=True, predicted_positive=False, actual_positive=False),
    Row(vulnerable=True, predicted_positive=False, actual_positive=False),
    Row(vulnerable=False, predicted_positive=True, actual_positive=True),
    Row(vulnerable=False, predicted_positive=True, actual_positive=True),
    Row(vulnerable=False, predicted_positive=True, actual_positive=False),  # other FP
    Row(vulnerable=False, predicted_positive=False, actual_positive=False),
)


def test_weighted_harm_score_with_default_weights():
    score = weighted_harm_score(_ROWS, WeightConfig())

    # 1 vulnerable FN * 3.0 + 1 other FP * 1.0 = 4.0
    assert score == pytest.approx(4.0)


def test_weighted_harm_score_with_custom_weights():
    weights = WeightConfig(
        fn_weight_vulnerable=10.0,
        fp_weight_vulnerable=1.0,
        fn_weight_other=1.0,
        fp_weight_other=2.0,
    )

    score = weighted_harm_score(_ROWS, weights)

    # 1 vulnerable FN * 10.0 + 1 other FP * 2.0 = 12.0
    assert score == pytest.approx(12.0)


def test_weighted_harm_score_ignores_correct_predictions():
    all_correct = (
        Row(vulnerable=True, predicted_positive=True, actual_positive=True),
        Row(vulnerable=False, predicted_positive=False, actual_positive=False),
    )

    score = weighted_harm_score(all_correct, WeightConfig())

    assert score == pytest.approx(0.0)


def test_weighted_harm_score_raises_on_missing_ground_truth():
    rows = (Row(vulnerable=True, predicted_positive=True, actual_positive=None),)

    with pytest.raises(ValueError, match="missing ground truth"):
        weighted_harm_score(rows, WeightConfig())
