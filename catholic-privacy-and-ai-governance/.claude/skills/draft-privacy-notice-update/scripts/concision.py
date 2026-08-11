"""Enforces build-plan.md §2.2: minimum sufficient documentation, not maximum
coverage. Every check here is a warning, never a failure — auto-cutting a
compliance document risks removing something genuinely needed, which is a
worse failure than a slightly long one. These are nudges for a human (or the
model, before it renders) to reconsider, not a gate.

The word-count thresholds below are a starting heuristic, not a tuned
standard — refine them against real assessments once the flagship skill has
actually been run, per agentskills.io's "refine with real execution"
guidance already cited in build-plan.md.
"""

from __future__ import annotations

from typing import Any

RATING_FIELD_WORD_LIMIT = 80
COMPLIANCE_BASE_WORDS = 100
COMPLIANCE_WORDS_PER_APPLICABLE_FRAMEWORK = 150
CST_REFLECTION_WORD_LIMIT = 250


def _word_count(text: str) -> int:
    return len(text.split())


def _lint_compliance_and_cst_reflection(record: dict[str, Any]) -> list[str]:
    """Shared by every shape this project validates: the compliance-length
    allowance scales with how many frameworks were actually marked
    applicable, and the CST reflection has a flat guideline. Both
    lint_assessment (the rubric-scored shape) and lint_triage (the
    triage shape) share this field pair, so the check lives once here.
    """
    warnings: list[str] = []

    applicable_count = sum(
        1 for f in record.get("frameworks_considered", []) if f.get("applicable")
    )
    compliance_limit = COMPLIANCE_BASE_WORDS + COMPLIANCE_WORDS_PER_APPLICABLE_FRAMEWORK * max(
        applicable_count, 1
    )
    compliance_count = _word_count(record.get("compliance", ""))
    if compliance_count > compliance_limit:
        warnings.append(
            f"compliance is {compliance_count} words against {applicable_count} "
            f"applicable framework(s) (guideline: {compliance_limit} words) — "
            "reconsider before finalizing (§2.2)."
        )

    cst_reflection_count = _word_count(record.get("cst_reflection", ""))
    if cst_reflection_count > CST_REFLECTION_WORD_LIMIT:
        warnings.append(
            f"cst_reflection is {cst_reflection_count} words — past the "
            f"{CST_REFLECTION_WORD_LIMIT}-word guideline (§2.2)."
        )

    return warnings


def lint_assessment(assessment: dict[str, Any]) -> list[str]:
    """Returns a list of non-fatal concision warnings; an empty list means
    nothing stood out as unusually long.
    """
    warnings: list[str] = []

    for rating in assessment.get("ratings", []):
        dimension_id = rating.get("dimension_id", "<unknown dimension>")
        for field in ("rationale", "mitigation", "ideal"):
            value = rating.get(field)
            if not value:
                continue
            count = _word_count(value)
            if count > RATING_FIELD_WORD_LIMIT:
                warnings.append(
                    f"ratings[{dimension_id}].{field} is {count} words — past the "
                    f"{RATING_FIELD_WORD_LIMIT}-word generous guideline (§2.2). "
                    "Reread it for restated rubric text or padding."
                )

    warnings.extend(_lint_compliance_and_cst_reflection(assessment))
    return warnings


def lint_triage(triage: dict[str, Any]) -> list[str]:
    """Returns a list of non-fatal concision warnings for the triage shape
    (build-plan.md step 12); an empty list means nothing stood out as
    unusually long.
    """
    warnings: list[str] = []

    request_description = triage.get("request", {}).get("description", "")
    count = _word_count(request_description)
    if count > RATING_FIELD_WORD_LIMIT:
        warnings.append(
            f"request.description is {count} words — past the "
            f"{RATING_FIELD_WORD_LIMIT}-word generous guideline (§2.2)."
        )

    for gap in triage.get("gaps", []):
        gap_id = gap.get("id", "<unknown gap>")
        count = _word_count(gap.get("description", ""))
        if count > RATING_FIELD_WORD_LIMIT:
            warnings.append(
                f"gaps[{gap_id}].description is {count} words — past the "
                f"{RATING_FIELD_WORD_LIMIT}-word generous guideline (§2.2)."
            )

    deadline_basis = triage.get("governing_deadline", {}).get("basis", "")
    count = _word_count(deadline_basis)
    if count > RATING_FIELD_WORD_LIMIT:
        warnings.append(
            f"governing_deadline.basis is {count} words — past the "
            f"{RATING_FIELD_WORD_LIMIT}-word generous guideline (§2.2)."
        )

    warnings.extend(_lint_compliance_and_cst_reflection(triage))
    return warnings
