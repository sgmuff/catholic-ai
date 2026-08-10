from pathlib import Path

import yaml

from appeal_path_audit.channels import ChannelResponse
from appeal_path_audit.runner import audit_notices, main, probe_channel


def _write_rules(rules_dir: Path) -> None:
    rules_dir.mkdir(exist_ok=True)
    (rules_dir / "test-rules.yaml").write_text(
        yaml.safe_dump(
            {
                "items": [
                    {
                        "id": "requires-automated-word",
                        "framework": "test",
                        "description": "must say automated",
                        "severity": "high",
                        "check": "keyword_presence",
                        "check_args": {"required_substrings": ["automated"]},
                    }
                ]
            }
        )
    )


def _write_notices(notices_dir: Path) -> None:
    notices_dir.mkdir(exist_ok=True)
    (notices_dir / "loan-denial.txt").write_text("Your loan was denied by our automated system.")
    (notices_dir / "hiring-rejection.txt").write_text("We will not be moving forward.")


def test_audit_notices_scores_every_notice_against_every_rule(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    notices_dir = tmp_path / "notices"
    _write_rules(rules_dir)
    _write_notices(notices_dir)

    findings = audit_notices(notices_dir, rules_dir)

    by_subject = {f.subject_id: f for f in findings}
    assert by_subject["loan-denial"].verdict == "pass"
    assert by_subject["hiring-rejection"].verdict == "fail"


class _StubChannel:
    def __init__(self, response: ChannelResponse) -> None:
        self._response = response

    def submit(self) -> ChannelResponse:
        return self._response


def test_probe_channel_passes_when_status_and_marker_match():
    channel = _StubChannel(ChannelResponse(status_code=202, body='{"ticket_id": "T-1"}'))

    findings = probe_channel("loan-appeal", channel, 200, 299, "ticket_id")

    reachability, review = findings
    assert reachability.verdict == "pass"
    assert review.verdict == "needs_review"


def test_probe_channel_fails_when_status_out_of_range():
    channel = _StubChannel(ChannelResponse(status_code=404, body="not found"))

    findings = probe_channel("loan-appeal", channel, 200, 299, None)

    assert findings[0].verdict == "fail"
    assert "404" in findings[0].explanation


def test_probe_channel_fails_when_marker_missing():
    channel = _StubChannel(ChannelResponse(status_code=200, body="thanks!"))

    findings = probe_channel("loan-appeal", channel, 200, 299, "ticket_id")

    assert findings[0].verdict == "fail"
    assert "ticket_id" in findings[0].explanation


def test_main_audit_notices_end_to_end(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    notices_dir = tmp_path / "notices"
    out_dir = tmp_path / "reports"
    _write_rules(rules_dir)
    _write_notices(notices_dir)

    exit_code = main(
        [
            "audit-notices",
            "--notices-dir",
            str(notices_dir),
            "--rules-dir",
            str(rules_dir),
            "--out-dir",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    assert list(out_dir.glob("*-run.md"))


def test_main_audit_notices_fails_on_bad_rules_dir(tmp_path: Path):
    notices_dir = tmp_path / "notices"
    _write_notices(notices_dir)

    exit_code = main(
        [
            "audit-notices",
            "--notices-dir",
            str(notices_dir),
            "--rules-dir",
            str(tmp_path / "does-not-exist"),
            "--out-dir",
            str(tmp_path / "reports"),
        ]
    )

    assert exit_code == 1


def test_main_probe_channel_fails_on_bad_config(tmp_path: Path):
    bad_config = tmp_path / "channel.yaml"
    bad_config.write_text(yaml.safe_dump({"id": "loan-appeal"}))  # missing url/payload

    exit_code = main(
        [
            "probe-channel",
            "--channel-config",
            str(bad_config),
            "--out-dir",
            str(tmp_path / "reports"),
        ]
    )

    assert exit_code == 1


def test_main_audit_notices_fails_on_empty_rules_dir(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    notices_dir = tmp_path / "notices"
    _write_notices(notices_dir)

    exit_code = main(
        [
            "audit-notices",
            "--notices-dir",
            str(notices_dir),
            "--rules-dir",
            str(rules_dir),
            "--out-dir",
            str(tmp_path / "reports"),
        ]
    )

    assert exit_code == 1


class _FakeChannel:
    def submit(self) -> ChannelResponse:
        return ChannelResponse(status_code=202, body='{"ticket_id": "T-1"}')


def _fake_channel_factory(
    url: str, payload: dict[str, object], method: str, headers: dict[str, str] | None
) -> _FakeChannel:
    return _FakeChannel()


def test_main_probe_channel_end_to_end(tmp_path: Path):
    config_path = tmp_path / "channel.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "id": "loan-appeal",
                "url": "https://example.test/api/appeals",
                "payload": {"applicant_id": "TEST-0001"},
                "confirmation_marker": "ticket_id",
            }
        )
    )
    out_dir = tmp_path / "reports"

    exit_code = main(
        ["probe-channel", "--channel-config", str(config_path), "--out-dir", str(out_dir)],
        channel_factory=_fake_channel_factory,
    )

    assert exit_code == 0
    reports = list(out_dir.glob("*-run.md"))
    assert len(reports) == 1
    assert "loan-appeal" in reports[0].read_text()
