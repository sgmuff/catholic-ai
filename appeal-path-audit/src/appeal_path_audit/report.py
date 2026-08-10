"""The shape of an audit run's results, and how they're rendered and
written. A report is findings, not a certification — a clean run over the
notices and channels actually tested says nothing about ones that weren't.
`needs_review` findings are never resolved automatically; the report always
says so and carries the captured detail a person needs to make that call.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

Verdict = Literal["pass", "fail", "needs_review"]
Kind = Literal["notice", "channel"]

_DISCLAIMER = (
    "This is a record of which notices and channels passed, failed, or need human review — not "
    "a certification. A 'pass' means the specific rule or channel tested checked out, nothing "
    "broader. Every `needs_review` finding requires a person to read the captured detail and "
    "judge it — in particular, no finding here claims to verify that a human genuinely "
    "reconsidered a case, only that a channel accepted and acknowledged a request."
)


@dataclass(frozen=True)
class Finding:
    subject_id: str
    kind: Kind
    rule_id: str | None
    severity: str
    verdict: Verdict
    explanation: str
    detail: str


def _summary_line(findings: tuple[Finding, ...]) -> str:
    total = len(findings)
    failed = [f for f in findings if f.verdict == "fail"]
    needs_review = [f for f in findings if f.verdict == "needs_review"]
    passed = total - len(failed) - len(needs_review)

    parts = [f"{passed} of {total} findings passed"]
    if failed:
        named = ", ".join(
            f"{f.subject_id}/{f.rule_id}" if f.rule_id else f.subject_id for f in failed
        )
        parts.append(f"{len(failed)} failed: {named}")
    if needs_review:
        named = ", ".join(f.subject_id for f in needs_review)
        parts.append(f"{len(needs_review)} need human review: {named}")
    return "; ".join(parts) + "."


def _blockquote(text: str) -> list[str]:
    lines = [f"> {line}" if line else ">" for line in text.splitlines()]
    return lines or [">"]


def render_markdown(findings: tuple[Finding, ...], generated_at: datetime) -> str:
    lines = [
        "# Appeal-path audit report",
        "",
        _DISCLAIMER,
        "",
        f"- Generated: {generated_at.isoformat()}",
        f"- Findings: {len(findings)}",
        "",
        "## At a glance",
        "",
        _summary_line(findings),
        "",
    ]

    for kind, heading in (("notice", "## Notice findings"), ("channel", "## Channel findings")):
        subset = [f for f in findings if f.kind == kind]
        if not subset:
            continue
        lines.append(heading)
        lines.append("")
        for finding in subset:
            title = f"{finding.subject_id}"
            if finding.rule_id:
                title += f" — {finding.rule_id}"
            lines.append(f"### {title}: {finding.verdict} ({finding.severity})")
            lines.append("")
            lines.append(finding.explanation)
            lines.append("")
            if finding.detail:
                lines.append("Detail:")
                lines.append("")
                lines.extend(_blockquote(finding.detail))
                lines.append("")

    return "\n".join(lines)


_INDEX_HEADER = (
    "# Appeal-path audit run index\n\n"
    "Every report generated in this directory, oldest first.\n\n"
    "| Date | Findings | Failed | Needs review | Report |\n"
    "| --- | --- | --- | --- | --- |\n"
)


def _update_index(
    out_dir: Path, findings: tuple[Finding, ...], generated_at: datetime, report_path: Path
) -> None:
    index_path = out_dir / "INDEX.md"
    if not index_path.exists():
        index_path.write_text(_INDEX_HEADER)
    failed = sum(1 for f in findings if f.verdict == "fail")
    needs_review = sum(1 for f in findings if f.verdict == "needs_review")
    date = generated_at.strftime("%Y-%m-%d")
    row = f"| {date} | {len(findings)} | {failed} | {needs_review} | [{report_path.name}]({report_path.name}) |\n"
    with index_path.open("a") as f:
        f.write(row)


def write_report(findings: tuple[Finding, ...], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    generated_at = now_utc()
    date = generated_at.strftime("%Y-%m-%d-%H%M%S")
    path = out_dir / f"{date}-run.md"
    suffix = 2
    while path.exists():
        path = out_dir / f"{date}-run-{suffix}.md"
        suffix += 1
    path.write_text(render_markdown(findings, generated_at))
    _update_index(out_dir, findings, generated_at, path)
    return path


def now_utc() -> datetime:
    return datetime.now(UTC)
