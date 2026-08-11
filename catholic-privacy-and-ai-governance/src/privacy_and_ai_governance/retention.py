"""Validates a retention/reassessment-entry JSON. A fifth task shape,
deliberately the smallest in this project: one inventory entry (a data
element, or an AI system) checked against its own stated review interval,
producing a single verdict — `current`, `needs-review`, `needs-update`, or
`retire` — rather than a score, a deadline list, or a checklist
(build-plan.md step 18). Resisted padding this to match its siblings'
size; a single-entry check doesn't need more structure than this.

Same discipline as its siblings: the model does the judgment (whether the
entry is still justified); this module only checks the judgment is
internally consistent.
"""

from __future__ import annotations

import datetime
from typing import Any

from privacy_and_ai_governance.language import ComplianceLanguageError, check_compliance_language

VERDICT_ACTIONS = {"current", "needs-review", "needs-update", "retire"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_date(value: Any) -> datetime.date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def validate_retention_entry(
    record: dict[str, Any],
    *,
    known_framework_ids: set[str],
) -> list[str]:
    """Returns every validation problem found; an empty list means the
    entry is internally consistent. Never raises — the caller decides
    whether the errors are fatal.
    """
    errors: list[str] = []

    if not _nonempty(record.get("title")):
        errors.append("title must not be empty")

    entry = record.get("entry", {})
    for field in ("description", "category", "purpose"):
        if not _nonempty(entry.get(field)):
            errors.append(f"entry.{field} must not be empty")
    if _parse_date(entry.get("last_reviewed_date")) is None:
        errors.append("entry.last_reviewed_date must be a valid ISO date (YYYY-MM-DD)")

    frameworks_considered = record.get("frameworks_considered", [])
    if not frameworks_considered:
        errors.append(
            "frameworks_considered must list every framework considered, "
            "including ones ruled inapplicable"
        )
    seen_framework_ids: set[str] = set()
    for fw in frameworks_considered:
        fid = fw.get("id")
        if fid not in known_framework_ids:
            errors.append(
                f"frameworks_considered references unknown framework id "
                f"'{fid}' — it must be an entry in references/frameworks/index.md"
            )
        elif fid in seen_framework_ids:
            errors.append(f"frameworks_considered lists '{fid}' more than once")
        seen_framework_ids.add(fid)
        if not _nonempty(fw.get("basis")):
            errors.append(
                f"frameworks_considered['{fid}'] must state a basis for its "
                "applicability determination"
            )

    verdict = record.get("verdict")
    if not verdict:
        errors.append("verdict is required")
    else:
        action = verdict.get("action")
        if action not in VERDICT_ACTIONS:
            errors.append(
                f"verdict.action must be one of {sorted(VERDICT_ACTIONS)}, got {action!r}"
            )
        if not _nonempty(verdict.get("rationale")):
            errors.append("verdict.rationale must not be empty")
        target_date = verdict.get("target_date")
        if action == "current":
            if target_date is not None and _parse_date(target_date) is None:
                errors.append("verdict.target_date must be a valid ISO date (YYYY-MM-DD) or null")
        elif action in VERDICT_ACTIONS and _parse_date(target_date) is None:
            errors.append(
                f"verdict.target_date must be a valid ISO date (YYYY-MM-DD) when "
                f"action is {action!r}"
            )

    compliance = record.get("compliance", "")
    if not _nonempty(compliance):
        errors.append("compliance must not be empty")
    else:
        try:
            check_compliance_language(compliance)
        except ComplianceLanguageError as exc:
            errors.append(str(exc))

    if not _nonempty(record.get("cst_reflection")):
        errors.append("cst_reflection must not be empty")

    return errors
