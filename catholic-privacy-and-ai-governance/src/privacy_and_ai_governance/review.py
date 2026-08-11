"""Validates a vendor-review JSON. A fourth task shape, distinct from
assessment.py's rubric-scored one, triage.py's single-governing-deadline
one, and incident.py's parallel-notification-obligations one: reviewing a
vendor's documentation against a fixed checklist isn't scored on a 1-5
scale (there's no "3 out of 5" for whether a DPA exists), and it isn't a
point-in-time event with a deadline — it's a per-item satisfied/partial/
missing determination against a baseline (build-plan.md step 16),
each item requiring evidence or a gap description depending on its
status, plus optional remediation commitments and a reassessment date.

Same discipline as its siblings throughout: the model does the judgment
(what the vendor's documentation actually shows, per item); this module
only checks the judgment is internally consistent.
"""

from __future__ import annotations

import datetime
from typing import Any

from privacy_and_ai_governance.language import ComplianceLanguageError, check_compliance_language

BASELINE_ITEM_STATUSES = {"satisfied", "partial", "missing"}
REMEDIATION_STATUSES = {"open", "complete"}
RISK_LEVELS = {"low", "moderate", "high", "critical"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_date(value: Any) -> datetime.date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def validate_review(
    review: dict[str, Any],
    *,
    known_framework_ids: set[str],
    known_baseline_item_ids: list[str],
) -> list[str]:
    """Returns every validation problem found; an empty list means the
    review record is internally consistent. Never raises — the caller
    decides whether the errors are fatal.
    """
    errors: list[str] = []

    if not _nonempty(review.get("title")):
        errors.append("title must not be empty")

    vendor = review.get("vendor", {})
    if not _nonempty(vendor.get("name")):
        errors.append("vendor.name must not be empty")
    if not _nonempty(vendor.get("description")):
        errors.append("vendor.description must not be empty")

    frameworks_considered = review.get("frameworks_considered", [])
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
        seen_framework_ids.add(fid)
        if not _nonempty(entry.get("basis")):
            errors.append(
                f"frameworks_considered['{fid}'] must state a basis for its "
                "applicability determination"
            )

    baseline_items = review.get("baseline_items", [])
    seen_item_ids: list[str] = [item.get("id") for item in baseline_items]
    missing_items = [i for i in known_baseline_item_ids if i not in seen_item_ids]
    if missing_items:
        errors.append(f"missing baseline_items for: {', '.join(missing_items)}")
    unknown_items = sorted(
        {i for i in seen_item_ids if i is not None and i not in known_baseline_item_ids}
    )
    if unknown_items:
        errors.append(f"baseline_items reference unknown item(s): {', '.join(unknown_items)}")
    duplicate_items = sorted(
        {i for i in seen_item_ids if i is not None and seen_item_ids.count(i) > 1}
    )
    if duplicate_items:
        errors.append(
            f"baseline_items list the same item more than once: {', '.join(duplicate_items)}"
        )

    for item in baseline_items:
        item_id = item.get("id", "<unknown>")
        status = item.get("status")
        if status not in BASELINE_ITEM_STATUSES:
            errors.append(
                f"baseline_items[{item_id}].status must be one of "
                f"{sorted(BASELINE_ITEM_STATUSES)}, got {status!r}"
            )
            continue
        if status in ("satisfied", "partial") and not _nonempty(item.get("evidence")):
            errors.append(
                f"baseline_items[{item_id}].evidence is required when status is {status!r}"
            )
        if status in ("partial", "missing") and not _nonempty(item.get("gap")):
            errors.append(f"baseline_items[{item_id}].gap is required when status is {status!r}")

    for commitment in review.get("remediation_commitments", []):
        commitment_id = commitment.get("id", "<unknown>")
        if not _nonempty(commitment.get("description")):
            errors.append(f"remediation_commitments[{commitment_id}].description must not be empty")
        if _parse_date(commitment.get("target_date")) is None:
            errors.append(
                f"remediation_commitments[{commitment_id}].target_date must be a valid "
                "ISO date (YYYY-MM-DD)"
            )
        if commitment.get("status") not in REMEDIATION_STATUSES:
            errors.append(
                f"remediation_commitments[{commitment_id}].status must be one of "
                f"{sorted(REMEDIATION_STATUSES)}, got {commitment.get('status')!r}"
            )

    if _parse_date(review.get("reassessment_due")) is None:
        errors.append("reassessment_due must be a valid ISO date (YYYY-MM-DD)")

    overall_risk = review.get("overall_risk")
    if not overall_risk:
        errors.append("overall_risk is required")
    else:
        level = overall_risk.get("level")
        if level not in RISK_LEVELS:
            errors.append(f"overall_risk.level must be one of {sorted(RISK_LEVELS)}, got {level!r}")
        if not _nonempty(overall_risk.get("rationale")):
            errors.append("overall_risk.rationale must not be empty")

    compliance = review.get("compliance", "")
    if not _nonempty(compliance):
        errors.append("compliance must not be empty")
    else:
        try:
            check_compliance_language(compliance)
        except ComplianceLanguageError as exc:
            errors.append(str(exc))

    if not _nonempty(review.get("cst_reflection")):
        errors.append("cst_reflection must not be empty")

    return errors
