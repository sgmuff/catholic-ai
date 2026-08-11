"""Renders a validated assessment or triage record to Markdown. Compliance
always precedes the Catholic Social Teaching reflection, per build-plan.md
§2.1 — a reader who wants only the compliance content can act on it
without reading past it. Two renderers live here because two shapes exist
(build-plan.md step 12): render_markdown for the rubric-scored shape
(assessment.py), render_triage_markdown for the classify/deadline/gaps
shape (triage.py). write_report takes the renderer as a parameter rather
than each shape needing its own copy of the file-writing logic.
"""

from __future__ import annotations

import datetime
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

_SLUG_DISALLOWED_RE = re.compile(r"[^A-Za-z0-9-]+")


def slugify(title: str) -> str:
    """Turns a title into a hyphenated slug: spaces become hyphens, anything
    that isn't a letter, digit, or hyphen is dropped, and runs of hyphens
    collapse to one.
    """
    hyphenated = title.replace(" ", "-")
    stripped = _SLUG_DISALLOWED_RE.sub("-", hyphenated)
    collapsed = re.sub(r"-+", "-", stripped)
    return collapsed.strip("-")


def render_markdown(assessment: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# {assessment['title']}")
    lines.append("")
    lines.append(
        "*Advisory draft, grounded in a working interpretation of the frameworks "
        "considered below — not a legal opinion. Requires review and approval by "
        "an accountable person before the underlying activity proceeds.*"
    )
    lines.append("")

    subject = assessment["subject"]
    lines.append("## Subject")
    lines.append("")
    lines.append(f"- **Description:** {subject['description']}")
    lines.append(f"- **Purpose:** {subject['purpose']}")
    if subject.get("personal_data"):
        lines.append(f"- **Personal data:** {', '.join(subject['personal_data'])}")
    if subject.get("systems"):
        lines.append(f"- **Systems:** {', '.join(subject['systems'])}")
    if subject.get("recipients"):
        lines.append(f"- **Recipients:** {', '.join(subject['recipients'])}")
    lines.append(f"- **Retention:** {subject['retention']}")
    if subject.get("institution_context"):
        lines.append(f"- **Institution context:** {subject['institution_context']}")
    lines.append("")

    lines.append("## Frameworks considered")
    lines.append("")
    for framework in assessment["frameworks_considered"]:
        status = "Applicable" if framework.get("applicable") else "Not applicable"
        lines.append(f"- **{framework['id']}** — {status}: {framework['basis']}")
    lines.append("")

    lines.append("## Compliance")
    lines.append("")
    lines.append(assessment["compliance"])
    lines.append("")

    lines.append("## Rubric ratings")
    lines.append("")
    lines.append("| Dimension | Score | Contested |")
    lines.append("|---|---|---|")
    for rating in assessment["ratings"]:
        contested = "yes" if rating.get("contested") else ""
        lines.append(f"| {rating['dimension_id']} | {rating['score']}/5 | {contested} |")
    lines.append("")

    for rating in assessment["ratings"]:
        lines.append(f"### {rating['dimension_id']} — {rating['score']}/5")
        lines.append("")
        lines.append(f"**Rationale:** {rating['rationale']}")
        if rating.get("mitigation"):
            lines.append("")
            lines.append(f"**Mitigation:** {rating['mitigation']}")
        lines.append("")
        lines.append(f"**Ideal:** {rating['ideal']}")
        lines.append("")

    lines.append("## Catholic Social Teaching reflection")
    lines.append("")
    lines.append(assessment["cst_reflection"])
    lines.append("")

    return "\n".join(lines)


def render_triage_markdown(triage: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# {triage['title']}")
    lines.append("")
    lines.append(
        "*Advisory draft, grounded in a working interpretation of the frameworks "
        "considered below — not a legal opinion. Requires review and approval by "
        "an accountable person before a response is sent.*"
    )
    lines.append("")

    request = triage["request"]
    lines.append("## Request")
    lines.append("")
    lines.append(f"- **Description:** {request['description']}")
    lines.append(f"- **Type:** {request['request_type']}")
    if request.get("channel"):
        lines.append(f"- **Channel:** {request['channel']}")
    if request.get("received_date"):
        lines.append(f"- **Received:** {request['received_date']}")
    if request.get("requester_context"):
        lines.append(f"- **Requester context:** {request['requester_context']}")
    lines.append("")

    lines.append("## Frameworks considered")
    lines.append("")
    for framework in triage["frameworks_considered"]:
        status = "Applicable" if framework.get("applicable") else "Not applicable"
        lines.append(f"- **{framework['id']}** — {status}: {framework['basis']}")
    lines.append("")

    deadline = triage["governing_deadline"]
    lines.append("## Governing deadline")
    lines.append("")
    lines.append(f"**Response due: {deadline['response_due']}** ({deadline['citation']})")
    lines.append("")
    lines.append(deadline["basis"])
    lines.append("")

    lines.append("## Compliance")
    lines.append("")
    lines.append(triage["compliance"])
    lines.append("")

    lines.append("## Gaps and outstanding items")
    lines.append("")
    gaps = triage.get("gaps", [])
    if not gaps:
        lines.append("No outstanding gaps identified.")
    else:
        for gap in gaps:
            marker = "**Blocking.**" if gap.get("blocking") else "Non-blocking."
            lines.append(f"- {marker} {gap['description']}")
    lines.append("")

    lines.append("## Catholic Social Teaching reflection")
    lines.append("")
    lines.append(triage["cst_reflection"])
    lines.append("")

    return "\n".join(lines)


def write_report(
    record: dict[str, Any],
    out_dir: Path,
    render_fn: Callable[[dict[str, Any]], str] = render_markdown,
    today: datetime.date | None = None,
) -> Path:
    """Renders *record* with *render_fn* (the rubric-scored render_markdown
    by default, or render_triage_markdown for the triage shape) and writes
    it to ``<out_dir>/<YYYY-MM-DD>-<Slugified-Title>.md``, creating
    *out_dir* if needed. Returns the path written.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    date = today or datetime.datetime.now(tz=datetime.UTC).date()
    filename = f"{date.isoformat()}-{slugify(record['title'])}.md"
    path = out_dir / filename
    path.write_text(render_fn(record), encoding="utf-8")
    return path
