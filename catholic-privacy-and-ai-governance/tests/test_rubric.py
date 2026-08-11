from pathlib import Path

import pytest

from privacy_and_ai_governance.rubric import (
    RubricError,
    load_dimension_ids,
    load_passing_threshold,
)

REPO_CRITERIA_PATH = Path(__file__).parent.parent / "rubric" / "criteria.md"


class TestLoadDimensionIds:
    def test_loads_all_seven_dimensions_from_the_real_rubric(self) -> None:
        ids = load_dimension_ids(REPO_CRITERIA_PATH)
        assert ids == [
            "necessity-and-proportionality",
            "data-minimization",
            "lawful-basis-and-consent",
            "retention",
            "security-controls",
            "third-party-sharing",
            "human-oversight",
        ]

    def test_ignores_non_numbered_headings(self, tmp_path: Path) -> None:
        criteria = tmp_path / "criteria.md"
        criteria.write_text(
            "## How to score\n\nSome prose.\n\n"
            "## 1. Widget quality — `widget-quality`\n\nMore prose.\n"
        )
        assert load_dimension_ids(criteria) == ["widget-quality"]

    def test_raises_if_no_dimensions_found(self, tmp_path: Path) -> None:
        criteria = tmp_path / "criteria.md"
        criteria.write_text("## How to score\n\nNo dimensions here.\n")
        with pytest.raises(RubricError):
            load_dimension_ids(criteria)


class TestLoadPassingThreshold:
    def test_loads_threshold_from_the_real_rubric(self) -> None:
        assert load_passing_threshold(REPO_CRITERIA_PATH) == 4

    def test_raises_if_no_threshold_stated(self, tmp_path: Path) -> None:
        criteria = tmp_path / "criteria.md"
        criteria.write_text("## How to score\n\nNo threshold mentioned.\n")
        with pytest.raises(RubricError):
            load_passing_threshold(criteria)
