"""The shape of a probe run's results, and how they're rendered and written.
A report is findings, not a certification — passing every probe means the
target resisted the probes actually run, nothing more. `needs_review`
findings are never resolved automatically; the report says so plainly and
names the human step that has to happen next, the way `cst-finding`'s own
reports name the pastor or theologian who has to review a finding before
it's acted on.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from guardrail_probing.detectors import Verdict

_DISCLAIMER = (
    "This is a record of which probes passed, failed, or need human review — not a safety "
    "certification. A 'pass' means the target resisted the probes actually run in this corpus, "
    "not that it is invulnerable. Every `needs_review` finding requires a person to read the "
    "response and judge it before any deployment decision is made on it."
)


@dataclass(frozen=True)
class Finding:
    probe_id: str
    category: str
    severity: str
    verdict: Verdict
    response: str
    explanation: str


def _summary_line(findings: tuple[Finding, ...]) -> str:
    total = len(findings)
    failed = [f for f in findings if f.verdict == "fail"]
    needs_review = [f for f in findings if f.verdict == "needs_review"]
    passed = total - len(failed) - len(needs_review)

    parts = [f"{passed} of {total} probes passed"]
    if failed:
        named = ", ".join(f.probe_id for f in failed)
        parts.append(f"{len(failed)} failed: {named}")
    if needs_review:
        named = ", ".join(f.probe_id for f in needs_review)
        parts.append(f"{len(needs_review)} need human review: {named}")
    return "; ".join(parts) + "."


def _blockquote(text: str) -> list[str]:
    lines = [f"> {line}" if line else ">" for line in text.splitlines()]
    return lines or [">"]


def render_markdown(findings: tuple[Finding, ...], generated_at: datetime) -> str:
    lines = [
        "# Guardrail probe report",
        "",
        _DISCLAIMER,
        "",
        f"- Generated: {generated_at.isoformat()}",
        f"- Probes run: {len(findings)}",
        "",
        "## At a glance",
        "",
        _summary_line(findings),
        "",
        "## Findings by category",
        "",
    ]

    by_category: dict[str, list[Finding]] = {}
    for finding in findings:
        by_category.setdefault(finding.category, []).append(finding)

    for category in sorted(by_category):
        lines.append(f"### {category}")
        lines.append("")
        for finding in by_category[category]:
            lines.append(f"#### {finding.probe_id} — {finding.verdict} ({finding.severity})")
            lines.append("")
            lines.append(finding.explanation)
            lines.append("")
            lines.append("Response:")
            lines.append("")
            lines.extend(_blockquote(finding.response))
            lines.append("")

    return "\n".join(lines)


_INDEX_HEADER = (
    "# Guardrail probe run index\n\n"
    "Every report generated in this directory, oldest first.\n\n"
    "| Date | Probes | Failed | Needs review | Report |\n"
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
