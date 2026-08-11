#!/usr/bin/env python3
"""Validates an AI-governance assessment JSON against this skill's bundled
rubric and framework registry, then renders it to Markdown. The model does
the judgment; this script only checks the judgment is internally
consistent — it never scores anything itself. See SKILL.md step 4.

Dependency-free — standard library only — so it runs with a plain python3
wherever this skill is installed. Unlike the source project's own
src/privacy_and_ai_governance/assessment.py (which loads the framework
registry straight from YAML via PyYAML), this script reads
references/frameworks/index.json — a machine-readable rendering the sync
script produces specifically so this script never needs a YAML parser.
Everything else here (rubric parsing, the compliance/CST language boundary,
the concision lint, and Markdown rendering) is a byte-for-byte copy of that
project's own tested modules — see sibling files rubric.py, language.py,
concision.py, report.py in this same directory. This file itself is
identical to its privacy-domain sibling's own scripts/assessment.py — it
discovers its rubric file by name rather than hardcoding one, so the same
script works unchanged in either skill.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from concision import lint_assessment
from language import ComplianceLanguageError, check_compliance_language
from report import write_report

from rubric import load_dimension_ids, load_passing_threshold

SKILL_DIR = Path(__file__).resolve().parent.parent
REFERENCES_DIR = SKILL_DIR / "references"


class AssessmentError(Exception):
    """Raised when an assessment JSON fails validation. Carries every
    problem found, not just the first, so a fix pass can address them all at
    once.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("Could not build assessment:\n" + "\n".join(f"- {e}" for e in errors))


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_known_framework_ids(index_json_path: Path) -> set[str]:
    with index_json_path.open(encoding="utf-8") as f:
        records = json.load(f)
    return {record["id"] for record in records}


def validate_assessment(
    assessment: dict[str, Any],
    *,
    dimension_ids: list[str],
    passing_threshold: int,
    known_framework_ids: set[str],
) -> list[str]:
    """Returns every validation problem found; an empty list means the
    assessment is internally consistent. Never raises — the caller decides
    whether the errors are fatal.
    """
    errors: list[str] = []

    if not _nonempty(assessment.get("title")):
        errors.append("title must not be empty")

    subject = assessment.get("subject", {})
    for field in ("description", "purpose", "retention"):
        if not _nonempty(subject.get(field)):
            errors.append(f"subject.{field} must not be empty")

    frameworks_considered = assessment.get("frameworks_considered", [])
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

    ratings = assessment.get("ratings", [])
    rated_ids = [r.get("dimension_id") for r in ratings]
    missing = [d for d in dimension_ids if d not in rated_ids]
    if missing:
        errors.append(f"missing ratings for dimension(s): {', '.join(missing)}")
    unknown = sorted({d for d in rated_ids if d is not None and d not in dimension_ids})
    if unknown:
        errors.append(f"ratings reference unknown dimension(s): {', '.join(unknown)}")
    duplicates = sorted({d for d in rated_ids if d is not None and rated_ids.count(d) > 1})
    if duplicates:
        errors.append(f"ratings score the same dimension more than once: {', '.join(duplicates)}")

    for rating in ratings:
        dim = rating.get("dimension_id", "<unknown>")
        score = rating.get("score")
        if not isinstance(score, int) or isinstance(score, bool) or not (1 <= score <= 5):
            errors.append(f"ratings[{dim}].score must be an integer 1-5, got {score!r}")
            continue
        if not _nonempty(rating.get("rationale")):
            errors.append(f"ratings[{dim}].rationale must not be empty")
        if not _nonempty(rating.get("ideal")):
            errors.append(f"ratings[{dim}].ideal must not be empty")
        if not isinstance(rating.get("contested"), bool):
            errors.append(f"ratings[{dim}].contested must be present and a boolean")
        if score < passing_threshold and not _nonempty(rating.get("mitigation")):
            errors.append(
                f"ratings[{dim}] scored {score}, below the passing threshold of "
                f"{passing_threshold}, and has no mitigation"
            )

    compliance = assessment.get("compliance", "")
    if not _nonempty(compliance):
        errors.append("compliance must not be empty")
    else:
        try:
            check_compliance_language(compliance)
        except ComplianceLanguageError as exc:
            errors.append(str(exc))

    if not _nonempty(assessment.get("cst_reflection")):
        errors.append("cst_reflection must not be empty")

    return errors


def find_rubric_path() -> Path:
    """Every skill bundles exactly one rubric file under references/rubric/
    — discovered by name, not hardcoded, so this script is identical
    whichever skill it's copied into (draft-privacy-impact-assessment's
    rubric is named criteria.md; assess-ai-system-risk-tier's is
    ai-criteria.md).
    """
    candidates = sorted((REFERENCES_DIR / "rubric").glob("*.md"))
    if len(candidates) != 1:
        raise AssessmentError(
            [f"expected exactly one rubric file in references/rubric/, found {len(candidates)}"]
        )
    return candidates[0]


def load_and_validate(input_path: Path) -> tuple[dict[str, Any], list[str]]:
    """Loads an assessment JSON from *input_path* and validates it against
    this skill's own bundled rubric and framework index.

    Returns (assessment, concision_warnings) on success. Raises
    AssessmentError, carrying every problem found, if validation fails.
    """
    with input_path.open(encoding="utf-8") as f:
        assessment = json.load(f)

    rubric_path = find_rubric_path()
    dimension_ids = load_dimension_ids(rubric_path)
    passing_threshold = load_passing_threshold(rubric_path)
    known_framework_ids = load_known_framework_ids(REFERENCES_DIR / "frameworks" / "index.json")

    errors = validate_assessment(
        assessment,
        dimension_ids=dimension_ids,
        passing_threshold=passing_threshold,
        known_framework_ids=known_framework_ids,
    )
    if errors:
        raise AssessmentError(errors)

    warnings = lint_assessment(assessment)
    return assessment, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and render an AI-governance assessment.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        assessment, warnings = load_and_validate(args.input)
    except AssessmentError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"Could not build assessment: {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    written = write_report(assessment, args.out_dir)
    print(f"wrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
