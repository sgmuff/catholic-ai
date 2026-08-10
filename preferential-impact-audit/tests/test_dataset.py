from pathlib import Path

import pytest

from preferential_impact_audit.dataset import load_dataset

_CSV_WITH_LABELS = """income_bracket,approved,repaid
low,yes,yes
low,no,yes
high,yes,yes
high,yes,no
"""

_CSV_NO_LABELS = """income_bracket,approved
low,yes
high,no
"""


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_load_dataset_happy_path_with_labels(tmp_path: Path):
    path = _write(tmp_path / "data.csv", _CSV_WITH_LABELS)

    rows = load_dataset(
        path,
        protected_column="income_bracket",
        vulnerable_value="low",
        prediction_column="approved",
        positive_value="yes",
        label_column="repaid",
        positive_label_value="yes",
    )

    assert len(rows) == 4
    assert rows[0].vulnerable is True
    assert rows[0].predicted_positive is True
    assert rows[0].actual_positive is True
    assert rows[3].vulnerable is False
    assert rows[3].actual_positive is False


def test_load_dataset_happy_path_without_labels(tmp_path: Path):
    path = _write(tmp_path / "data.csv", _CSV_NO_LABELS)

    rows = load_dataset(
        path,
        protected_column="income_bracket",
        vulnerable_value="low",
        prediction_column="approved",
        positive_value="yes",
    )

    assert len(rows) == 2
    assert all(r.actual_positive is None for r in rows)


def test_load_dataset_raises_on_missing_column(tmp_path: Path):
    path = _write(tmp_path / "data.csv", _CSV_NO_LABELS)

    with pytest.raises(ValueError, match="missing required column"):
        load_dataset(
            path,
            protected_column="income_bracket",
            vulnerable_value="low",
            prediction_column="does_not_exist",
            positive_value="yes",
        )


def test_load_dataset_raises_when_only_label_column_given(tmp_path: Path):
    path = _write(tmp_path / "data.csv", _CSV_WITH_LABELS)

    with pytest.raises(ValueError, match="given together"):
        load_dataset(
            path,
            protected_column="income_bracket",
            vulnerable_value="low",
            prediction_column="approved",
            positive_value="yes",
            label_column="repaid",
        )


def test_load_dataset_raises_on_empty_file(tmp_path: Path):
    path = _write(tmp_path / "data.csv", "income_bracket,approved\n")

    with pytest.raises(ValueError, match="no data rows found"):
        load_dataset(
            path,
            protected_column="income_bracket",
            vulnerable_value="low",
            prediction_column="approved",
            positive_value="yes",
        )
