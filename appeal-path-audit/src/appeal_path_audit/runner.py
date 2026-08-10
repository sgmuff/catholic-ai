"""Two independent checks, run separately: `audit-notices` checks whether
adverse-decision notice text discloses what it's legally required to;
`probe-channel` checks whether a documented appeal channel actually accepts
and acknowledges a submission. Neither claims to verify that a human
genuinely reconsidered a case — see `channels.py` and `report.py`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Protocol

from appeal_path_audit.channels import Channel, HttpFormChannel, load_channel_config
from appeal_path_audit.checks import CHECKS
from appeal_path_audit.notices import load_notices
from appeal_path_audit.report import Finding, write_report
from appeal_path_audit.rules import load_rules


def audit_notices(notices_dir: Path, rules_dir: Path) -> tuple[Finding, ...]:
    rules = load_rules(rules_dir)
    notices = load_notices(notices_dir)
    findings = []
    for notice in sorted(notices.values(), key=lambda n: n.id):
        for rule in sorted(rules.values(), key=lambda r: r.id):
            result = CHECKS[rule.check](rule.check_args, notice.text)
            findings.append(
                Finding(
                    subject_id=notice.id,
                    kind="notice",
                    rule_id=rule.id,
                    severity=rule.severity,
                    verdict=result.verdict,
                    explanation=result.explanation,
                    detail=notice.text,
                )
            )
    return tuple(findings)


def probe_channel(
    channel_id: str,
    channel: Channel,
    expected_status_min: int,
    expected_status_max: int,
    confirmation_marker: str | None,
) -> tuple[Finding, ...]:
    response = channel.submit()
    status_ok = expected_status_min <= response.status_code <= expected_status_max
    marker_ok = confirmation_marker is None or confirmation_marker in response.body
    reachable = status_ok and marker_ok

    if not status_ok:
        explanation = (
            f"status {response.status_code} is outside the expected range "
            f"[{expected_status_min}, {expected_status_max}]"
        )
    elif not marker_ok:
        explanation = f"response did not contain confirmation marker {confirmation_marker!r}"
    else:
        explanation = f"status {response.status_code} within expected range; channel is reachable"

    reachability = Finding(
        subject_id=channel_id,
        kind="channel",
        rule_id=None,
        severity="high",
        verdict="pass" if reachable else "fail",
        explanation=explanation,
        detail=response.body,
    )
    human_review = Finding(
        subject_id=channel_id,
        kind="channel",
        rule_id=None,
        severity="medium",
        verdict="needs_review",
        explanation=(
            "reachability alone doesn't establish that a human will genuinely reconsider the "
            "case — read the captured response and judge that separately"
        ),
        detail=response.body,
    )
    return (reachability, human_review)


def _run_audit_notices(args: argparse.Namespace) -> int:
    try:
        findings = audit_notices(args.notices_dir, args.rules_dir)
    except ValueError as exc:
        print(f"Could not audit notices: {exc}", file=sys.stderr)
        return 1
    path = write_report(findings, args.out_dir)
    print(f"Report written to {path}")
    return 0


def _run_probe_channel(args: argparse.Namespace) -> int:
    try:
        config = load_channel_config(args.channel_config)
    except ValueError as exc:
        print(f"Could not load channel config: {exc}", file=sys.stderr)
        return 1

    channel = args.channel_factory(
        url=config.url, payload=config.payload, method=config.method, headers=config.headers
    )
    try:
        findings = probe_channel(
            config.id,
            channel,
            config.expected_status_min,
            config.expected_status_max,
            config.confirmation_marker,
        )
    except OSError as exc:
        print(f"Run failed: {exc}", file=sys.stderr)
        return 1

    path = write_report(findings, args.out_dir)
    print(f"Report written to {path}")
    return 0


class ChannelFactory(Protocol):
    def __call__(
        self, url: str, payload: dict[str, object], method: str, headers: dict[str, str] | None
    ) -> Channel: ...


def main(argv: list[str] | None = None, channel_factory: ChannelFactory = HttpFormChannel) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit-notices")
    audit_parser.add_argument("--notices-dir", type=Path, required=True)
    audit_parser.add_argument("--rules-dir", type=Path, default=Path("rules"))
    audit_parser.add_argument("--out-dir", type=Path, default=Path("reports"))
    audit_parser.set_defaults(func=_run_audit_notices)

    probe_parser = subparsers.add_parser("probe-channel")
    probe_parser.add_argument("--channel-config", type=Path, required=True)
    probe_parser.add_argument("--out-dir", type=Path, default=Path("reports"))
    probe_parser.set_defaults(func=_run_probe_channel)

    args = parser.parse_args(argv)
    args.channel_factory = channel_factory
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
