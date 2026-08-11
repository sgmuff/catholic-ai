#!/usr/bin/env python3
"""Validates a rights-request triage JSON against this skill's bundled
framework registry, then renders it to Markdown. The model does the
judgment — classification, deadline calculation, gap-finding; this script
only checks the judgment is internally consistent. See SKILL.md step 3.

Dependency-free — standard library only — so it runs with a plain python3
wherever this skill is installed. Unlike the source project's own
src/privacy_and_ai_governance/triage.py (which loads the framework
registry straight from YAML via PyYAML), this script reads
references/frameworks/index.json — a machine-readable rendering the sync
script produces specifically so this script never needs a YAML parser.
Everything else here (the compliance/CST language boundary, the concision
lint, and Markdown rendering) is a byte-for-byte copy of that project's own
tested modules — see sibling files language.py, concision.py, report.py in
this same directory. Unlike its sibling skills' assessment.py, this skill
has no rubric.py copy: there's no rubric here to parse.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

from concision import lint_triage
from language import ComplianceLanguageError, check_compliance_language
from report import render_triage_markdown, write_report

SKILL_DIR = Path(__file__).resolve().parent.parent
REFERENCES_DIR = SKILL_DIR / "references"


class TriageError(Exception):
    """Raised when a triage JSON fails validation. Carries every problem
    found, not just the first, so a fix pass can address them all at once.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("Could not build triage record:\n" + "\n".join(f"- {e}" for e in errors))


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
        gfid = governing_deadline.get("framework_id")
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


def load_and_validate(input_path: Path) -> tuple[dict[str, Any], list[str]]:
    """Loads a triage JSON from *input_path* and validates it against this
    skill's own bundled framework index.

    Returns (triage, concision_warnings) on success. Raises TriageError,
    carrying every problem found, if validation fails.
    """
    with input_path.open(encoding="utf-8") as f:
        triage = json.load(f)

    known_framework_ids = load_known_framework_ids(REFERENCES_DIR / "frameworks" / "index.json")

    errors = validate_triage(triage, known_framework_ids=known_framework_ids)
    if errors:
        raise TriageError(errors)

    warnings = lint_triage(triage)
    return triage, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and render a rights-request triage.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        triage, warnings = load_and_validate(args.input)
    except TriageError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"Could not build triage record: {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    written = write_report(triage, args.out_dir, render_fn=render_triage_markdown)
    print(f"wrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
