from datetime import UTC, datetime
from pathlib import Path

from appeal_path_audit.report import Finding, render_markdown, write_report

_GENERATED_AT = datetime(2026, 8, 10, 12, 0, 0, tzinfo=UTC)

_FINDINGS = (
    Finding(
        subject_id="loan-denial",
        kind="notice",
        rule_id="gdpr-art22-automation-disclosure",
        severity="high",
        verdict="pass",
        explanation="required substring present: ['automated']",
        detail="Your application was denied by our automated decision system.",
    ),
    Finding(
        subject_id="loan-denial",
        kind="notice",
        rule_id="gdpr-art22-human-review-right",
        severity="high",
        verdict="fail",
        explanation="none of the required substring(s) present",
        detail="Your application was denied by our automated decision system.",
    ),
    Finding(
        subject_id="loan-appeal-channel",
        kind="channel",
        rule_id=None,
        severity="high",
        verdict="needs_review",
        explanation="channel accepted the request; response requires human judgment",
        detail='{"ticket_id": "T-1", "message": "We received your request."}',
    ),
)


def test_render_markdown_summary_line_counts_each_verdict():
    markdown = render_markdown(_FINDINGS, _GENERATED_AT)

    assert "1 of 3 findings passed" in markdown
    assert "1 failed: loan-denial/gdpr-art22-human-review-right" in markdown
    assert "1 need human review: loan-appeal-channel" in markdown


def test_render_markdown_groups_findings_by_kind():
    markdown = render_markdown(_FINDINGS, _GENERATED_AT)

    assert "## Notice findings" in markdown
    assert "## Channel findings" in markdown
    assert "### loan-denial — gdpr-art22-automation-disclosure: pass (high)" in markdown
    assert "### loan-appeal-channel: needs_review (high)" in markdown


def test_render_markdown_includes_disclaimer_and_detail_text():
    markdown = render_markdown(_FINDINGS, _GENERATED_AT)

    assert "not a certification" in markdown
    assert "ticket_id" in markdown


def test_write_report_creates_file_and_index(tmp_path: Path):
    path = write_report(_FINDINGS, tmp_path)

    assert path.exists()
    assert "loan-denial" in path.read_text()
    index = (tmp_path / "INDEX.md").read_text()
    assert "| 3 | 1 | 1 |" in index
    assert path.name in index


def test_write_report_does_not_collide_on_repeat_calls(tmp_path: Path):
    first = write_report(_FINDINGS, tmp_path)
    second = write_report(_FINDINGS, tmp_path)

    assert first != second
    assert first.exists()
    assert second.exists()
