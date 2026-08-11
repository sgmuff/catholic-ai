#!/usr/bin/env python3
"""Validates an AI regulatory-change-mapping JSON against this skill's
bundled framework registry, then renders it to Markdown. The model does the
judgment — what the development means, which frameworks it touches, what
should change; this script only checks the judgment is internally
consistent. See SKILL.md step 3.

Dependency-free — standard library only — so it runs with a plain python3
wherever this skill is installed. Unlike the source project's own
src/privacy_and_ai_governance/regulatory_change.py (which loads the
framework registry straight from YAML via PyYAML), this script reads
references/frameworks/index.json — a machine-readable rendering the sync
script produces specifically so this script never needs a YAML parser.
Everything else here (the compliance/CST language boundary, the concision
lint, and Markdown rendering) is a byte-for-byte copy of that project's own
tested modules — see sibling files language.py, concision.py, report.py in
this same directory. No rubric.py, no baseline.py — this shape uses
neither.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

from concision import lint_regulatory_change
from language import ComplianceLanguageError, check_compliance_language
from report import render_regulatory_change_markdown, write_report

SKILL_DIR = Path(__file__).resolve().parent.parent
REFERENCES_DIR = SKILL_DIR / "references"

ACTION_TYPES = {
    "register-new-framework",
    "update-required-element",
    "retire-framework",
    "no-action",
}
ACTION_TYPES_REQUIRING_FRAMEWORK_ID = {"update-required-element", "retire-framework"}
ACTION_TYPES_REJECTING_FRAMEWORK_ID = {"register-new-framework", "no-action"}


class RegulatoryChangeError(Exception):
    """Raised when a regulatory-change JSON fails validation. Carries every
    problem found, not just the first, so a fix pass can address them all
    at once.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(
            "Could not build regulatory change mapping:\n" + "\n".join(f"- {e}" for e in errors)
        )


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


def load_and_validate(input_path: Path) -> tuple[dict[str, Any], list[str]]:
    """Loads a regulatory-change JSON from *input_path* and validates it
    against this skill's own bundled framework index.

    Returns (record, concision_warnings) on success. Raises
    RegulatoryChangeError, carrying every problem found, if validation
    fails.
    """
    with input_path.open(encoding="utf-8") as f:
        record = json.load(f)

    known_framework_ids = load_known_framework_ids(REFERENCES_DIR / "frameworks" / "index.json")

    errors = validate_regulatory_change(record, known_framework_ids=known_framework_ids)
    if errors:
        raise RegulatoryChangeError(errors)

    warnings = lint_regulatory_change(record)
    return record, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and render an AI regulatory-change mapping."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        record, warnings = load_and_validate(args.input)
    except RegulatoryChangeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"Could not build regulatory change mapping: {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    written = write_report(record, args.out_dir, render_fn=render_regulatory_change_markdown)
    print(f"wrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
