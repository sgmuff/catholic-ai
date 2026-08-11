#!/usr/bin/env python3
"""Validates a vendor-review JSON against this skill's bundled framework
registry and baseline checklist, then renders it to Markdown. The model
does the judgment — what the vendor's documentation actually shows, per
baseline item, and the overall risk level; this script only checks the
judgment is internally consistent. See SKILL.md step 4.

Dependency-free — standard library only — so it runs with a plain python3
wherever this skill is installed. Unlike the source project's own
src/privacy_and_ai_governance/review.py (which loads the framework
registry straight from YAML via PyYAML), this script reads
references/frameworks/index.json — a machine-readable rendering the sync
script produces specifically so this script never needs a YAML parser.
Everything else here (baseline-item-id parsing, the compliance/CST
language boundary, the concision lint, and Markdown rendering) is a
byte-for-byte copy of that project's own tested modules — see sibling
files baseline.py, language.py, concision.py, report.py in this same
directory. Unlike its triage/incident-shaped siblings, this skill has a
baseline.py copy but, like them, no rubric.py — there's no rubric here to
parse.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

from baseline import BaselineError, load_baseline_item_ids
from concision import lint_review
from language import ComplianceLanguageError, check_compliance_language
from report import render_review_markdown, write_report

SKILL_DIR = Path(__file__).resolve().parent.parent
REFERENCES_DIR = SKILL_DIR / "references"

BASELINE_ITEM_STATUSES = {"satisfied", "partial", "missing"}
REMEDIATION_STATUSES = {"open", "complete"}
RISK_LEVELS = {"low", "moderate", "high", "critical"}


class ReviewError(Exception):
    """Raised when a review JSON fails validation. Carries every problem
    found, not just the first, so a fix pass can address them all at once.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("Could not build review:\n" + "\n".join(f"- {e}" for e in errors))


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_date(value: Any) -> datetime.date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def load_known_framework_ids(index_json_path: Path) -> set[str]:
    with index_json_path.open(encoding="utf-8") as f:
        records = json.load(f)
    return {record["id"] for record in records}


def find_baseline_path() -> Path:
    """Every review-shaped skill bundles exactly one baseline file under
    references/baseline/ — discovered by name, not hardcoded, so this
    script is identical whichever skill it's copied into.
    """
    candidates = sorted((REFERENCES_DIR / "baseline").glob("*.md"))
    if len(candidates) != 1:
        raise ReviewError(
            [f"expected exactly one baseline file in references/baseline/, found {len(candidates)}"]
        )
    return candidates[0]


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


def load_and_validate(input_path: Path) -> tuple[dict[str, Any], list[str]]:
    """Loads a review JSON from *input_path* and validates it against this
    skill's own bundled framework index and baseline checklist.

    Returns (review, concision_warnings) on success. Raises ReviewError,
    carrying every problem found, if validation fails.
    """
    with input_path.open(encoding="utf-8") as f:
        review = json.load(f)

    baseline_path = find_baseline_path()
    try:
        known_baseline_item_ids = load_baseline_item_ids(baseline_path)
    except BaselineError as exc:
        raise ReviewError([str(exc)]) from exc
    known_framework_ids = load_known_framework_ids(REFERENCES_DIR / "frameworks" / "index.json")

    errors = validate_review(
        review,
        known_framework_ids=known_framework_ids,
        known_baseline_item_ids=known_baseline_item_ids,
    )
    if errors:
        raise ReviewError(errors)

    warnings = lint_review(review)
    return review, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and render a vendor privacy review.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        review, warnings = load_and_validate(args.input)
    except ReviewError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"Could not build review: {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    written = write_report(review, args.out_dir, render_fn=render_review_markdown)
    print(f"wrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
