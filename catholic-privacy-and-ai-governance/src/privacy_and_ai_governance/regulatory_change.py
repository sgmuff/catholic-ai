"""Validates a regulatory-change-mapping JSON. A sixth task shape: unlike
every prior shape, this one doesn't evaluate an institution's own
activity, system, vendor, or inventory entry — it ingests an external
input (a pasted regulatory or standards development) and maps its impact
against this project's own `frameworks/index.yaml` (build-plan.md step
18). `frameworks_considered` here asks a different question than its
siblings' own version of that field: not "does this framework apply to
the institution" but "does this development change what an already-
registered framework requires" — named `impacted`, not `applicable`, to
keep that distinction honest. `recommended_actions` is the deliverable:
a diff against the registry, not a finding about a person or system.

Same discipline as its siblings: the model does the judgment (what the
development means, which frameworks it touches, what should change);
this module only checks the judgment is internally consistent.
"""

from __future__ import annotations

import datetime
from typing import Any

from privacy_and_ai_governance.language import ComplianceLanguageError, check_compliance_language

ACTION_TYPES = {
    "register-new-framework",
    "update-required-element",
    "retire-framework",
    "no-action",
}
ACTION_TYPES_REQUIRING_FRAMEWORK_ID = {"update-required-element", "retire-framework"}
ACTION_TYPES_REJECTING_FRAMEWORK_ID = {"register-new-framework", "no-action"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_date(value: Any) -> datetime.date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def validate_regulatory_change(
    record: dict[str, Any],
    *,
    known_framework_ids: set[str],
) -> list[str]:
    """Returns every validation problem found; an empty list means the
    mapping is internally consistent. Never raises — the caller decides
    whether the errors are fatal.
    """
    errors: list[str] = []

    if not _nonempty(record.get("title")):
        errors.append("title must not be empty")

    development = record.get("development", {})
    for field in ("source", "summary"):
        if not _nonempty(development.get(field)):
            errors.append(f"development.{field} must not be empty")
    if _parse_date(development.get("published_date")) is None:
        errors.append("development.published_date must be a valid ISO date (YYYY-MM-DD)")

    frameworks_considered = record.get("frameworks_considered", [])
    if not frameworks_considered:
        errors.append(
            "frameworks_considered must list every framework considered, "
            "including ones ruled not impacted"
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
                f"frameworks_considered['{fid}'] must state a basis for its impact determination"
            )

    recommended_actions = record.get("recommended_actions", [])
    if not recommended_actions:
        errors.append(
            "recommended_actions must record at least one action, including "
            "'no-action' if nothing needs to change"
        )
    for action in recommended_actions:
        action_id = action.get("id", "<unknown>")
        action_type = action.get("type")
        if action_type not in ACTION_TYPES:
            errors.append(
                f"recommended_actions[{action_id}].type must be one of "
                f"{sorted(ACTION_TYPES)}, got {action_type!r}"
            )
            continue
        if not _nonempty(action.get("description")):
            errors.append(f"recommended_actions[{action_id}].description must not be empty")
        framework_id = action.get("framework_id")
        if action_type in ACTION_TYPES_REQUIRING_FRAMEWORK_ID:
            if framework_id not in known_framework_ids:
                errors.append(
                    f"recommended_actions[{action_id}].framework_id must be a known "
                    f"framework id when type is {action_type!r}, got {framework_id!r}"
                )
        elif action_type in ACTION_TYPES_REJECTING_FRAMEWORK_ID and framework_id is not None:
            errors.append(
                f"recommended_actions[{action_id}].framework_id must be null when "
                f"type is {action_type!r}"
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
