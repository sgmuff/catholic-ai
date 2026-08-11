"""Validates a privacy-incident triage JSON. A third task shape, distinct
from both assessment.py's rubric-scored one and triage.py's single-
governing-deadline one: an incident can trigger several independent,
simultaneous notification obligations to different audiences (a
supervisory authority, affected individuals, a state attorney general) —
none of which "governs" over the others the way a single requester's
response deadline does in triage.py. Force-fitting this into
triage.py's `governing_deadline` would have lost that plurality; this
module models it directly instead, per build-plan.md's own discipline of
designing a task shape deliberately rather than stretching an existing one.

Same discipline as its siblings throughout: the model does the judgment
(severity, which obligations apply, each deadline); this module only
checks the judgment is internally consistent.
"""

from __future__ import annotations

import datetime
from typing import Any

from privacy_and_ai_governance.language import ComplianceLanguageError, check_compliance_language

SEVERITY_LEVELS = {"low", "moderate", "high", "critical"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_date(value: Any) -> datetime.date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def validate_incident(
    incident: dict[str, Any],
    *,
    known_framework_ids: set[str],
) -> list[str]:
    """Returns every validation problem found; an empty list means the
    incident record is internally consistent. Never raises — the caller
    decides whether the errors are fatal.
    """
    errors: list[str] = []

    if not _nonempty(incident.get("title")):
        errors.append("title must not be empty")

    facts = incident.get("incident", {})
    if not _nonempty(facts.get("description")):
        errors.append("incident.description must not be empty")
    discovered_date = _parse_date(facts.get("discovered_date"))
    if discovered_date is None:
        errors.append("incident.discovered_date must be a valid ISO date (YYYY-MM-DD)")

    known_applicable_ids: set[str] = set()
    frameworks_considered = incident.get("frameworks_considered", [])
    if not frameworks_considered:
        errors.append(
            "frameworks_considered must list every framework considered, "
            "including ones ruled inapplicable"
        )
    seen_framework_ids: set[str] = set()
    for entry in frameworks_considered:
        fid = entry.get("id")
        if fid not in known_framework_ids:
            errors.append(
                f"frameworks_considered references unknown framework id "
                f"'{fid}' — it must be an entry in references/frameworks/index.md"
            )
        elif fid in seen_framework_ids:
            errors.append(f"frameworks_considered lists '{fid}' more than once")
        else:
            if entry.get("applicable") is True:
                known_applicable_ids.add(fid)
        seen_framework_ids.add(fid)
        if not _nonempty(entry.get("basis")):
            errors.append(
                f"frameworks_considered['{fid}'] must state a basis for its "
                "applicability determination"
            )

    severity = incident.get("severity")
    if not severity:
        errors.append("severity is required")
    else:
        level = severity.get("level")
        if level not in SEVERITY_LEVELS:
            errors.append(f"severity.level must be one of {sorted(SEVERITY_LEVELS)}, got {level!r}")
        if not _nonempty(severity.get("rationale")):
            errors.append("severity.rationale must not be empty")

    for obligation in incident.get("notification_obligations", []):
        oid = obligation.get("id", "<unknown>")
        fid = obligation.get("framework_id")
        if fid not in known_framework_ids:
            errors.append(
                f"notification_obligations[{oid}].framework_id references unknown "
                f"framework id '{fid}'"
            )
        elif fid not in known_applicable_ids:
            errors.append(
                f"notification_obligations[{oid}].framework_id '{fid}' must be marked "
                "applicable in frameworks_considered — an obligation can't come from a "
                "framework that was ruled inapplicable"
            )
        if not _nonempty(obligation.get("audience")):
            errors.append(f"notification_obligations[{oid}].audience must not be empty")
        if not _nonempty(obligation.get("citation")):
            errors.append(f"notification_obligations[{oid}].citation must not be empty")
        if not _nonempty(obligation.get("basis")):
            errors.append(f"notification_obligations[{oid}].basis must not be empty")
        due_date = _parse_date(obligation.get("due_date"))
        if due_date is None:
            errors.append(
                f"notification_obligations[{oid}].due_date must be a valid ISO date (YYYY-MM-DD)"
            )
        elif discovered_date is not None and due_date < discovered_date:
            errors.append(
                f"notification_obligations[{oid}].due_date must not be before "
                "incident.discovered_date"
            )

    for gap in incident.get("gaps", []):
        gap_id = gap.get("id", "<unknown>")
        if not _nonempty(gap.get("description")):
            errors.append(f"gaps[{gap_id}].description must not be empty")
        if not isinstance(gap.get("blocking"), bool):
            errors.append(f"gaps[{gap_id}].blocking must be present and a boolean")

    escalation = incident.get("escalation")
    if not escalation:
        errors.append("escalation is required")
    else:
        if not isinstance(escalation.get("required"), bool):
            errors.append("escalation.required must be present and a boolean")
        if not _nonempty(escalation.get("rationale")):
            errors.append("escalation.rationale must not be empty")

    compliance = incident.get("compliance", "")
    if not _nonempty(compliance):
        errors.append("compliance must not be empty")
    else:
        try:
            check_compliance_language(compliance)
        except ComplianceLanguageError as exc:
            errors.append(str(exc))

    if not _nonempty(incident.get("cst_reflection")):
        errors.append("cst_reflection must not be empty")

    return errors
