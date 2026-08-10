from datetime import UTC, datetime
from pathlib import Path

from preferential_impact_audit.metrics import GroupMetrics
from preferential_impact_audit.report import AuditReport, render_markdown, write_report
from preferential_impact_audit.weighting import WeightConfig

_GENERATED_AT = datetime(2026, 8, 10, 12, 0, 0, tzinfo=UTC)

_VULNERABLE = GroupMetrics(
    group="vulnerable", n=4, selection_rate=0.25, false_negative_rate=0.5, false_positive_rate=0.0
)
_OTHER = GroupMetrics(
    group="other", n=4, selection_rate=0.75, false_negative_rate=0.0, false_positive_rate=0.5
)
_DEFAULT_WEIGHTS = WeightConfig()


def _report(
    weighted_harm: float | None = 4.0, weights: WeightConfig | None = _DEFAULT_WEIGHTS
) -> AuditReport:
    return AuditReport(
        generated_at=_GENERATED_AT,
        vulnerable=_VULNERABLE,
        other=_OTHER,
        adverse_impact_ratio=0.25 / 0.75,
        weighted_harm=weighted_harm,
        weights=weights,
    )


def test_render_markdown_includes_standard_metrics_table():
    markdown = render_markdown(_report())

    assert "| Vulnerable | 25.0% | 50.0% | 0.0% |" in markdown
    assert "| Other | 75.0% | 0.0% | 50.0% |" in markdown


def test_render_markdown_flags_adverse_impact_below_four_fifths():
    markdown = render_markdown(_report())

    assert "Adverse impact flagged" in markdown


def test_render_markdown_does_not_flag_when_ratio_is_high():
    report = _report()
    report = AuditReport(
        generated_at=report.generated_at,
        vulnerable=report.vulnerable,
        other=GroupMetrics(
            group="other", n=4, selection_rate=0.3, false_negative_rate=0.0, false_positive_rate=0.5
        ),
        adverse_impact_ratio=0.9,
        weighted_harm=None,
        weights=None,
    )

    markdown = render_markdown(report)

    assert "No adverse impact flagged" in markdown


def test_render_markdown_includes_weighted_harm_when_present():
    markdown = render_markdown(_report())

    assert "Weighted harm score: 4.00" in markdown
    assert "preferential option for the poor" in markdown


def test_render_markdown_states_skip_reason_when_weighted_harm_absent():
    markdown = render_markdown(_report(weighted_harm=None, weights=None))

    assert "Skipped — no ground-truth label column was given" in markdown


def test_write_report_creates_file_and_index(tmp_path: Path):
    path = write_report(_report(), tmp_path)

    assert path.exists()
    assert "Weighted harm score" in path.read_text()
    index = (tmp_path / "INDEX.md").read_text()
    assert "yes" in index
    assert path.name in index


def test_write_report_does_not_collide_on_repeat_calls(tmp_path: Path):
    first = write_report(_report(), tmp_path)
    second = write_report(_report(), tmp_path)

    assert first != second
    assert first.exists()
    assert second.exists()
