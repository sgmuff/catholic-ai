#!/usr/bin/env python3
"""Validates an AI-incident triage JSON against this skill's bundled
framework registry, then renders it to Markdown. The model does the
judgment — severity, which notification obligations apply, each deadline,
whether to escalate; this script only checks the judgment is internally
consistent. See SKILL.md step 4.

Dependency-free — standard library only — so it runs with a plain python3
wherever this skill is installed. Unlike the source project's own
src/privacy_and_ai_governance/incident.py (which loads the framework
registry straight from YAML via PyYAML), this script reads
references/frameworks/index.json — a machine-readable rendering the sync
script produces specifically so this script never needs a YAML parser.
Everything else here (the compliance/CST language boundary, the concision
lint, and Markdown rendering) is a byte-for-byte copy of that project's own
tested modules — see sibling files language.py, concision.py, report.py in
this same directory. Like its sibling triage-privacy-rights-request, this
skill has no rubric.py copy: there's no rubric here to parse.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

from concision import lint_incident
from language import ComplianceLanguageError, check_compliance_language
from report import render_incident_markdown, write_report

SKILL_DIR = Path(__file__).resolve().parent.parent
REFERENCES_DIR = SKILL_DIR / "references"

SEVERITY_LEVELS = {"low", "moderate", "high", "critical"}


class IncidentError(Exception):
    """Raised when an incident JSON fails validation. Carries every problem
    found, not just the first, so a fix pass can address them all at once.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("Could not build incident record:\n" + "\n".join(f"- {e}" for e in errors))


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


def load_and_validate(input_path: Path) -> tuple[dict[str, Any], list[str]]:
    """Loads an incident JSON from *input_path* and validates it against
    this skill's own bundled framework index.

    Returns (incident, concision_warnings) on success. Raises
    IncidentError, carrying every problem found, if validation fails.
    """
    with input_path.open(encoding="utf-8") as f:
        incident = json.load(f)

    known_framework_ids = load_known_framework_ids(REFERENCES_DIR / "frameworks" / "index.json")

    errors = validate_incident(incident, known_framework_ids=known_framework_ids)
    if errors:
        raise IncidentError(errors)

    warnings = lint_incident(incident)
    return incident, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and render an AI-incident triage.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        incident, warnings = load_and_validate(args.input)
    except IncidentError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"Could not build incident record: {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    written = write_report(incident, args.out_dir, render_fn=render_incident_markdown)
    print(f"wrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
