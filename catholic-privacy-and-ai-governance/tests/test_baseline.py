from pathlib import Path

import pytest

from privacy_and_ai_governance.baseline import BaselineError, load_baseline_item_ids

REPO_ROOT = Path(__file__).parent.parent
PRIVACY_BASELINE = REPO_ROOT / "baselines" / "privacy-vendor.md"
AI_BASELINE = REPO_ROOT / "baselines" / "ai-vendor.md"


class TestLoadBaselineItemIds:
    def test_loads_every_item_id_from_the_real_privacy_baseline(self) -> None:
        ids = load_baseline_item_ids(PRIVACY_BASELINE)
        assert ids == [
            "dpa-in-place",
            "sub-processor-disclosure",
            "security-controls-evidence",
            "breach-notification-commitment",
            "data-return-deletion",
            "audit-rights",
            "data-transfer-mechanism",
            "minimum-necessary-scope",
        ]

    def test_loads_every_item_id_from_the_real_ai_baseline(self) -> None:
        ids = load_baseline_item_ids(AI_BASELINE)
        assert ids == [
            "model-documentation-provided",
            "evaluation-results-provided",
            "incident-reporting-commitment",
            "upstream-dependency-disclosure",
            "human-oversight-support",
            "update-notification-commitment",
            "data-governance-evidence",
        ]

    def test_raises_on_a_file_with_no_headings(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty.md"
        empty.write_text("# Nothing here\n\nJust prose.\n")
        with pytest.raises(BaselineError):
            load_baseline_item_ids(empty)

    def test_preserves_document_order_not_alphabetical_order(self, tmp_path: Path) -> None:
        doc = tmp_path / "baseline.md"
        doc.write_text(
            "## 1. Zebra item — `zebra-item`\n\nSome text.\n\n"
            "## 2. Apple item — `apple-item`\n\nMore text.\n"
        )
        assert load_baseline_item_ids(doc) == ["zebra-item", "apple-item"]
