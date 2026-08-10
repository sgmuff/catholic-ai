from pathlib import Path

from preferential_impact_audit.runner import main

_CSV_WITH_LABELS = """income_bracket,approved,repaid
low,yes,yes
low,no,yes
low,no,no
low,no,no
high,yes,yes
high,yes,yes
high,yes,no
high,no,no
"""

_CSV_NO_LABELS = """income_bracket,approved
low,yes
low,no
high,yes
high,no
"""


def test_main_end_to_end_with_labels_computes_weighted_score(tmp_path: Path):
    data = tmp_path / "data.csv"
    data.write_text(_CSV_WITH_LABELS)
    out_dir = tmp_path / "reports"

    exit_code = main(
        [
            "--data",
            str(data),
            "--protected-column",
            "income_bracket",
            "--vulnerable-value",
            "low",
            "--prediction-column",
            "approved",
            "--positive-value",
            "yes",
            "--label-column",
            "repaid",
            "--positive-label-value",
            "yes",
            "--out-dir",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    reports = list(out_dir.glob("*-run.md"))
    assert len(reports) == 1
    assert "Weighted harm score" in reports[0].read_text()
    assert "Skipped" not in reports[0].read_text()


def test_main_end_to_end_without_labels_skips_weighted_score(tmp_path: Path):
    data = tmp_path / "data.csv"
    data.write_text(_CSV_NO_LABELS)
    out_dir = tmp_path / "reports"

    exit_code = main(
        [
            "--data",
            str(data),
            "--protected-column",
            "income_bracket",
            "--vulnerable-value",
            "low",
            "--prediction-column",
            "approved",
            "--positive-value",
            "yes",
            "--out-dir",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    reports = list(out_dir.glob("*-run.md"))
    assert "Skipped" in reports[0].read_text()


def test_main_respects_custom_weights(tmp_path: Path):
    data = tmp_path / "data.csv"
    data.write_text(_CSV_WITH_LABELS)
    out_dir = tmp_path / "reports"

    exit_code = main(
        [
            "--data",
            str(data),
            "--protected-column",
            "income_bracket",
            "--vulnerable-value",
            "low",
            "--prediction-column",
            "approved",
            "--positive-value",
            "yes",
            "--label-column",
            "repaid",
            "--positive-label-value",
            "yes",
            "--fn-weight-vulnerable",
            "10",
            "--out-dir",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    report_text = next(iter(out_dir.glob("*-run.md"))).read_text()
    assert "×10.0" in report_text


def test_main_fails_on_missing_column(tmp_path: Path):
    data = tmp_path / "data.csv"
    data.write_text(_CSV_NO_LABELS)

    exit_code = main(
        [
            "--data",
            str(data),
            "--protected-column",
            "does_not_exist",
            "--vulnerable-value",
            "low",
            "--prediction-column",
            "approved",
            "--positive-value",
            "yes",
            "--out-dir",
            str(tmp_path / "reports"),
        ]
    )

    assert exit_code == 1
