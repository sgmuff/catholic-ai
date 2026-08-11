#!/usr/bin/env python3
"""Validates a retention-entry JSON against this skill's bundled framework
registry, then renders it to Markdown. The model does the judgment —
whether the entry's retention is still justified; this script only checks
the judgment is internally consistent. See SKILL.md step 3.

Dependency-free — standard library only — so it runs with a plain python3
wherever this skill is installed. Unlike the source project's own
src/privacy_and_ai_governance/retention.py (which loads the framework
registry straight from YAML via PyYAML), this script reads
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

from concision import lint_retention_entry
from language import ComplianceLanguageError, check_compliance_language
from report import render_retention_markdown, write_report

SKILL_DIR = Path(__file__).resolve().parent.parent
REFERENCES_DIR = SKILL_DIR / "references"

VERDICT_ACTIONS = {"current", "needs-review", "needs-update", "retire"}


class RetentionEntryError(Exception):
    """Raised when a retention-entry JSON fails validation. Carries every
    problem found, not just the first, so a fix pass can address them all
    at once.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("Could not build retention entry:\n" + "\n".join(f"- {e}" for e in errors))


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


def load_and_validate(input_path: Path) -> tuple[dict[str, Any], list[str]]:
    """Loads a retention-entry JSON from *input_path* and validates it
    against this skill's own bundled framework index.

    Returns (record, concision_warnings) on success. Raises
    RetentionEntryError, carrying every problem found, if validation fails.
    """
    with input_path.open(encoding="utf-8") as f:
        record = json.load(f)

    known_framework_ids = load_known_framework_ids(REFERENCES_DIR / "frameworks" / "index.json")

    errors = validate_retention_entry(record, known_framework_ids=known_framework_ids)
    if errors:
        raise RetentionEntryError(errors)

    warnings = lint_retention_entry(record)
    return record, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and render a data-retention entry.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        record, warnings = load_and_validate(args.input)
    except RetentionEntryError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"Could not build retention entry: {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    written = write_report(record, args.out_dir, render_fn=render_retention_markdown)
    print(f"wrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
