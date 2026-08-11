"""Validates a DPIA assessment JSON against the rubric, the framework
registry, and the §2.1 compliance/CST language boundary (build-plan.md §7.2
step 4). The model does the judgment; this module only checks the judgment
is internally consistent — it never scores anything itself.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from privacy_and_ai_governance.concision import lint_assessment
from privacy_and_ai_governance.frameworks import active_frameworks, load_framework_registry
from privacy_and_ai_governance.language import ComplianceLanguageError, check_compliance_language
from privacy_and_ai_governance.rubric import load_dimension_ids, load_passing_threshold


class AssessmentError(Exception):
    """Raised when an assessment JSON fails validation. Carries every
    problem found, not just the first, so a fix pass can address them all at
    once — matching the "Could not build assessment" pattern this project's
    validators use throughout.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("Could not build assessment:\n" + "\n".join(f"- {e}" for e in errors))


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_assessment(
    assessment: dict[str, Any],
    *,
    dimension_ids: list[str],
    passing_threshold: int,
    framework_records: list[dict[str, Any]],
) -> list[str]:
    """Returns every validation problem found; an empty list means the
    assessment is internally consistent. Never raises — callers decide
    whether the errors are fatal.
    """
    errors: list[str] = []

    if not _nonempty(assessment.get("title")):
        errors.append("title must not be empty")

    subject = assessment.get("subject", {})
    for field in ("description", "purpose", "retention"):
        if not _nonempty(subject.get(field)):
            errors.append(f"subject.{field} must not be empty")

    known_ids = {r["id"] for r in framework_records}
    frameworks_considered = assessment.get("frameworks_considered", [])
    if not frameworks_considered:
        errors.append(
            "frameworks_considered must list every framework considered, "
            "including ones ruled inapplicable"
        )
    seen_framework_ids: set[str] = set()
    for entry in frameworks_considered:
        fid = entry.get("id")
        if fid not in known_ids:
            errors.append(
                f"frameworks_considered references unknown framework id "
                f"'{fid}' — it must be an active entry in frameworks/index.yaml"
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


def load_and_validate(
    input_path: Path,
    frameworks_dir: Path,
    rubric_path: Path,
    domain: str = "privacy",
) -> tuple[dict[str, Any], list[str]]:
    """Loads an assessment JSON from *input_path* and validates it against
    the rubric at *rubric_path* and the framework registry at
    *frameworks_dir*, filtered to *domain*.

    Returns (assessment, concision_warnings) on success. Raises
    AssessmentError, carrying every problem found, if validation fails.
    """
    with input_path.open(encoding="utf-8") as f:
        assessment = json.load(f)

    dimension_ids = load_dimension_ids(rubric_path)
    passing_threshold = load_passing_threshold(rubric_path)
    records = active_frameworks(load_framework_registry(frameworks_dir), domain=domain)

    errors = validate_assessment(
        assessment,
        dimension_ids=dimension_ids,
        passing_threshold=passing_threshold,
        framework_records=records,
    )
    if errors:
        raise AssessmentError(errors)

    warnings = lint_assessment(assessment)
    return assessment, warnings
