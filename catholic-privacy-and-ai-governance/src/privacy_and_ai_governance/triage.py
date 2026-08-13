"""Validates a rights-request (or, for a sibling incident-triage skill,
an incident) triage JSON. A deliberately different shape from
assessment.py's rubric-scored one: build-plan.md's own step 12 flagged
that a point-in-time request or incident doesn't map onto "score seven
ongoing-quality dimensions" the way a processing activity or an AI system
does. This module is that different shape, built rather than force-fit.

Same discipline as assessment.py throughout: the model does the judgment
(classification, deadline calculation, gap-finding); this module only
checks the judgment is internally consistent.
"""

from __future__ import annotations

import datetime
from typing import Any

from privacy_and_ai_governance.language import ComplianceLanguageError, check_compliance_language


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_date(value: Any) -> datetime.date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def validate_triage(
    triage: dict[str, Any],
    *,
    known_framework_ids: set[str],
) -> list[str]:
    """Returns every validation problem found; an empty list means the
    triage record is internally consistent. Never raises — the caller
    decides whether the errors are fatal.
    """
    errors: list[str] = []

    if not _nonempty(triage.get("title")):
        errors.append("title must not be empty")

    request = triage.get("request", {})
    for field in ("description", "request_type"):
        if not _nonempty(request.get(field)):
            errors.append(f"request.{field} must not be empty")
    received_date = _parse_date(request.get("received_date"))
    if received_date is None:
        errors.append("request.received_date must be a valid ISO date (YYYY-MM-DD)")

    known_applicable_ids: set[str] = set()
    frameworks_considered = triage.get("frameworks_considered", [])
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

    governing_deadline = triage.get("governing_deadline")
    if not governing_deadline:
        errors.append("governing_deadline is required")
    else:
        statutory = governing_deadline.get("statutory")
        if not isinstance(statutory, bool):
            errors.append("governing_deadline.statutory must be present and a boolean")

        gfid = governing_deadline.get("framework_id")
        if statutory is False:
            if gfid is not None:
                errors.append(
                    "governing_deadline.framework_id must be null when statutory is "
                    "false — an internal target can't be attributed to a framework "
                    "that doesn't actually govern it"
                )
            if known_applicable_ids:
                errors.append(
                    "governing_deadline.statutory may only be false when no framework "
                    "in frameworks_considered is marked applicable — "
                    f"{sorted(known_applicable_ids)} is/are applicable here, so its/their "
                    "deadline governs and can't be sidestepped"
                )
        else:
            if gfid not in known_framework_ids:
                errors.append(
                    f"governing_deadline.framework_id references unknown framework id '{gfid}'"
                )
            elif gfid not in known_applicable_ids:
                errors.append(
                    f"governing_deadline.framework_id '{gfid}' must be marked applicable "
                    "in frameworks_considered — a deadline can't be governed by a "
                    "framework that was ruled inapplicable"
                )

        if not _nonempty(governing_deadline.get("citation")):
            errors.append("governing_deadline.citation must not be empty")
        if not _nonempty(governing_deadline.get("basis")):
            errors.append("governing_deadline.basis must not be empty")
        response_due = _parse_date(governing_deadline.get("response_due"))
        if response_due is None:
            errors.append("governing_deadline.response_due must be a valid ISO date (YYYY-MM-DD)")
        elif received_date is not None and response_due < received_date:
            errors.append(
                "governing_deadline.response_due must not be before request.received_date"
            )

    for gap in triage.get("gaps", []):
        gap_id = gap.get("id", "<unknown>")
        if not _nonempty(gap.get("description")):
            errors.append(f"gaps[{gap_id}].description must not be empty")
        if not isinstance(gap.get("blocking"), bool):
            errors.append(f"gaps[{gap_id}].blocking must be present and a boolean")

    compliance = triage.get("compliance", "")
    if not _nonempty(compliance):
        errors.append("compliance must not be empty")
    else:
        try:
            check_compliance_language(compliance)
        except ComplianceLanguageError as exc:
            errors.append(str(exc))

    if not _nonempty(triage.get("cst_reflection")):
        errors.append("cst_reflection must not be empty")

    return errors
