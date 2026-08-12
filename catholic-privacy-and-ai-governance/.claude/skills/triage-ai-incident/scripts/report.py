"""Renders a validated assessment, triage, incident, review, retention-
entry, or regulatory-change record to Markdown. In five of the six
shapes, compliance precedes the Catholic Social Teaching reflection, per
build-plan.md §2.1 — a reader who wants only the compliance content can
act on it without reading past it. render_markdown is the deliberate
exception (build-plan.md §2.1 amendment, build sequence step 20): its CST
section leads, right after the title, as a Catholic executive summary of
what the assessment found — the compliance/rubric-ratings content that
follows is still the section a reader who wants only that can act on
without needing anything above it. Six renderers live here because six
shapes exist (build-plan.md steps 12, 14, 16, and 18): render_markdown
for the rubric-scored shape (assessment.py), render_triage_markdown for
the single-governing-deadline classify/deadline/gaps shape (triage.py),
render_incident_markdown for the shape with several independent,
simultaneous notification obligations (incident.py),
render_review_markdown for the per-item satisfied/partial/missing
baseline-check shape (review.py), render_retention_markdown for the
single-verdict inventory-entry shape (retention.py), and
render_regulatory_change_markdown for the impact-diff-against-the-
registry shape (regulatory_change.py). write_report takes the renderer
as a parameter rather than each shape needing its own copy of the
file-writing logic.
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

    lines.append("## Catholic Social Teaching summary")
    lines.append("")
    lines.append(assessment["cst_reflection"])
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


def render_incident_markdown(incident: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# {incident['title']}")
    lines.append("")
    lines.append(
        "*Advisory draft, grounded in a working interpretation of the frameworks "
        "considered below — not a legal opinion. Requires review and approval by "
        "an accountable person before any notification is sent.*"
    )
    lines.append("")

    facts = incident["incident"]
    lines.append("## Incident")
    lines.append("")
    lines.append(f"- **Description:** {facts['description']}")
    lines.append(f"- **Discovered:** {facts['discovered_date']}")
    if facts.get("affected_systems"):
        lines.append(f"- **Affected systems:** {', '.join(facts['affected_systems'])}")
    if facts.get("data_types"):
        lines.append(f"- **Data types:** {', '.join(facts['data_types'])}")
    if facts.get("individuals_affected_estimate") is not None:
        lines.append(
            f"- **Individuals affected (estimate):** {facts['individuals_affected_estimate']}"
        )
    lines.append("")

    lines.append("## Frameworks considered")
    lines.append("")
    for framework in incident["frameworks_considered"]:
        status = "Applicable" if framework.get("applicable") else "Not applicable"
        lines.append(f"- **{framework['id']}** — {status}: {framework['basis']}")
    lines.append("")

    severity = incident["severity"]
    lines.append("## Severity")
    lines.append("")
    lines.append(f"**{severity['level'].capitalize()}.** {severity['rationale']}")
    lines.append("")

    lines.append("## Notification obligations")
    lines.append("")
    obligations = incident.get("notification_obligations", [])
    if not obligations:
        lines.append("No notification obligation identified.")
    else:
        for obligation in obligations:
            lines.append(
                f"- **{obligation['audience']}** — due {obligation['due_date']} "
                f"({obligation['citation']}): {obligation['basis']}"
            )
    lines.append("")

    lines.append("## Compliance")
    lines.append("")
    lines.append(incident["compliance"])
    lines.append("")

    lines.append("## Gaps and outstanding items")
    lines.append("")
    gaps = incident.get("gaps", [])
    if not gaps:
        lines.append("No outstanding gaps identified.")
    else:
        for gap in gaps:
            marker = "**Blocking.**" if gap.get("blocking") else "Non-blocking."
            lines.append(f"- {marker} {gap['description']}")
    lines.append("")

    escalation = incident["escalation"]
    lines.append("## Escalation")
    lines.append("")
    verdict = "Required." if escalation.get("required") else "Not required."
    lines.append(f"**{verdict}** {escalation['rationale']}")
    lines.append("")

    lines.append("## Catholic Social Teaching reflection")
    lines.append("")
    lines.append(incident["cst_reflection"])
    lines.append("")

    return "\n".join(lines)


def render_review_markdown(review: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# {review['title']}")
    lines.append("")
    lines.append(
        "*Advisory draft, grounded in a working interpretation of the frameworks "
        "considered below — not a legal opinion. Requires review and approval by "
        "an accountable person before this review is relied on.*"
    )
    lines.append("")

    vendor = review["vendor"]
    lines.append("## Vendor")
    lines.append("")
    lines.append(f"- **Name:** {vendor['name']}")
    lines.append(f"- **Description:** {vendor['description']}")
    if vendor.get("service_provided"):
        lines.append(f"- **Service provided:** {vendor['service_provided']}")
    lines.append("")

    lines.append("## Frameworks considered")
    lines.append("")
    for framework in review["frameworks_considered"]:
        status = "Applicable" if framework.get("applicable") else "Not applicable"
        lines.append(f"- **{framework['id']}** — {status}: {framework['basis']}")
    lines.append("")

    lines.append("## Baseline items")
    lines.append("")
    lines.append("| Item | Status |")
    lines.append("|---|---|")
    for item in review["baseline_items"]:
        lines.append(f"| {item['id']} | {item['status']} |")
    lines.append("")

    for item in review["baseline_items"]:
        lines.append(f"### {item['id']} — {item['status']}")
        lines.append("")
        if item.get("evidence"):
            lines.append(f"**Evidence:** {item['evidence']}")
            lines.append("")
        if item.get("gap"):
            lines.append(f"**Gap:** {item['gap']}")
            lines.append("")

    lines.append("## Compliance")
    lines.append("")
    lines.append(review["compliance"])
    lines.append("")

    lines.append("## Remediation commitments")
    lines.append("")
    commitments = review.get("remediation_commitments", [])
    if not commitments:
        lines.append("No open remediation commitments.")
    else:
        for commitment in commitments:
            lines.append(
                f"- **{commitment['status']}**, due {commitment['target_date']}: "
                f"{commitment['description']}"
            )
    lines.append("")

    overall_risk = review["overall_risk"]
    lines.append("## Overall risk")
    lines.append("")
    lines.append(f"**{overall_risk['level'].capitalize()}.** {overall_risk['rationale']}")
    lines.append("")
    lines.append(f"**Reassessment due: {review['reassessment_due']}**")
    lines.append("")

    lines.append("## Catholic Social Teaching reflection")
    lines.append("")
    lines.append(review["cst_reflection"])
    lines.append("")

    return "\n".join(lines)


def render_retention_markdown(record: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# {record['title']}")
    lines.append("")
    lines.append(
        "*Advisory draft, grounded in a working interpretation of the frameworks "
        "considered below — not a legal opinion. Requires review and approval by "
        "an accountable person before any action is taken.*"
    )
    lines.append("")

    entry = record["entry"]
    lines.append("## Entry")
    lines.append("")
    lines.append(f"- **Description:** {entry['description']}")
    lines.append(f"- **Category:** {entry['category']}")
    lines.append(f"- **Purpose:** {entry['purpose']}")
    lines.append(f"- **Last reviewed:** {entry['last_reviewed_date']}")
    lines.append("")

    lines.append("## Frameworks considered")
    lines.append("")
    for framework in record["frameworks_considered"]:
        status = "Applicable" if framework.get("applicable") else "Not applicable"
        lines.append(f"- **{framework['id']}** — {status}: {framework['basis']}")
    lines.append("")

    verdict = record["verdict"]
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"**{verdict['action']}.** {verdict['rationale']}")
    if verdict.get("target_date"):
        lines.append("")
        lines.append(f"**Target date: {verdict['target_date']}**")
    lines.append("")

    lines.append("## Compliance")
    lines.append("")
    lines.append(record["compliance"])
    lines.append("")

    lines.append("## Catholic Social Teaching reflection")
    lines.append("")
    lines.append(record["cst_reflection"])
    lines.append("")

    return "\n".join(lines)


def render_regulatory_change_markdown(record: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# {record['title']}")
    lines.append("")
    lines.append(
        "*Advisory draft, grounded in a working interpretation of the frameworks "
        "considered below — not a legal opinion. Requires review and approval by "
        "an accountable person before any registry change is made.*"
    )
    lines.append("")

    development = record["development"]
    lines.append("## Development")
    lines.append("")
    lines.append(f"- **Source:** {development['source']}")
    if development.get("citation"):
        lines.append(f"- **Citation:** {development['citation']}")
    lines.append(f"- **Published:** {development['published_date']}")
    lines.append("")
    lines.append(development["summary"])
    lines.append("")

    lines.append("## Frameworks considered")
    lines.append("")
    for framework in record["frameworks_considered"]:
        status = "Impacted" if framework.get("impacted") else "Not impacted"
        lines.append(f"- **{framework['id']}** — {status}: {framework['basis']}")
    lines.append("")

    lines.append("## Compliance")
    lines.append("")
    lines.append(record["compliance"])
    lines.append("")

    lines.append("## Recommended actions")
    lines.append("")
    for action in record["recommended_actions"]:
        target = f" ({action['framework_id']})" if action.get("framework_id") else ""
        lines.append(f"- **{action['type']}{target}:** {action['description']}")
    lines.append("")

    lines.append("## Catholic Social Teaching reflection")
    lines.append("")
    lines.append(record["cst_reflection"])
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
