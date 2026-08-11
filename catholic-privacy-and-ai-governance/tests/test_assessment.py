import json
from pathlib import Path

import pytest

from privacy_and_ai_governance.assessment import (
    AssessmentError,
    load_and_validate,
    validate_assessment,
)

REPO_ROOT = Path(__file__).parent.parent
DIMENSION_IDS = [
    "necessity-and-proportionality",
    "data-minimization",
    "lawful-basis-and-consent",
    "retention",
    "security-controls",
    "third-party-sharing",
    "human-oversight",
]
FRAMEWORK_RECORDS = [{"id": "gdpr-dpia", "domain": "privacy", "status": "active"}]


def _rating(dimension_id: str, score: int = 5, contested: bool = False) -> dict:
    return {
        "dimension_id": dimension_id,
        "score": score,
        "rationale": f"A grounded rationale for {dimension_id}.",
        "mitigation": None if score >= 4 else f"A concrete mitigation for {dimension_id}.",
        "ideal": f"The fuller ideal for {dimension_id}.",
        "contested": contested,
    }


def _valid_assessment(**overrides) -> dict:
    assessment = {
        "title": "Parish bulletin sign-up form",
        "subject": {
            "description": "A web form collecting email addresses for a weekly bulletin.",
            "personal_data": ["email address"],
            "purpose": "Sending the weekly parish bulletin.",
            "systems": ["Mailchimp"],
            "recipients": ["parish office staff", "Mailchimp (processor)"],
            "retention": "Kept until the parishioner unsubscribes; no other deletion trigger.",
            "institution_context": "A parish",
        },
        "frameworks_considered": [
            {
                "id": "gdpr-dpia",
                "applicable": True,
                "basis": "Parish serves EU-resident parishioners.",
            }
        ],
        "ratings": [_rating(d) for d in DIMENSION_IDS],
        "compliance": "Under GDPR Art. 35(7)(d), retention must be bounded; this activity ties it to unsubscribe.",
        "cst_reflection": "This keeps the parishioner's data tied to an active relationship, not indefinite.",
    }
    assessment.update(overrides)
    return assessment


class TestValidateAssessmentHappyPath:
    def test_a_well_formed_assessment_has_no_errors(self) -> None:
        errors = validate_assessment(
            _valid_assessment(),
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert errors == []


class TestValidateAssessmentSubject:
    def test_empty_retention_is_rejected(self) -> None:
        assessment = _valid_assessment()
        assessment["subject"]["retention"] = ""
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("retention" in e for e in errors)

    def test_missing_purpose_is_rejected(self) -> None:
        assessment = _valid_assessment()
        del assessment["subject"]["purpose"]
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("purpose" in e for e in errors)


class TestValidateAssessmentFrameworks:
    def test_unknown_framework_id_is_rejected(self) -> None:
        assessment = _valid_assessment()
        assessment["frameworks_considered"] = [
            {"id": "made-up-framework", "applicable": True, "basis": "x"}
        ]
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("made-up-framework" in e for e in errors)

    def test_empty_frameworks_considered_is_rejected(self) -> None:
        assessment = _valid_assessment()
        assessment["frameworks_considered"] = []
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("frameworks_considered" in e for e in errors)

    def test_missing_basis_is_rejected(self) -> None:
        assessment = _valid_assessment()
        assessment["frameworks_considered"] = [{"id": "gdpr-dpia", "applicable": True, "basis": ""}]
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("basis" in e for e in errors)


class TestValidateAssessmentRatings:
    def test_missing_dimension_is_rejected(self) -> None:
        assessment = _valid_assessment()
        assessment["ratings"] = [_rating(d) for d in DIMENSION_IDS if d != "retention"]
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("retention" in e and "missing" in e for e in errors)

    def test_unknown_dimension_is_rejected(self) -> None:
        assessment = _valid_assessment()
        assessment["ratings"].append(_rating("invented-dimension"))
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("invented-dimension" in e for e in errors)

    def test_duplicate_dimension_is_rejected(self) -> None:
        assessment = _valid_assessment()
        assessment["ratings"].append(_rating("retention"))
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("retention" in e and "more than once" in e for e in errors)

    def test_score_out_of_range_is_rejected(self) -> None:
        assessment = _valid_assessment()
        assessment["ratings"][0]["score"] = 9
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("score" in e for e in errors)

    def test_low_score_without_mitigation_is_rejected(self) -> None:
        assessment = _valid_assessment()
        assessment["ratings"][0]["score"] = 2
        assessment["ratings"][0]["mitigation"] = None
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("mitigation" in e for e in errors)

    def test_low_score_with_mitigation_passes(self) -> None:
        assessment = _valid_assessment()
        assessment["ratings"][0]["score"] = 2
        assessment["ratings"][0]["mitigation"] = (
            "Narrow the scope of collection to the stated purpose."
        )
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert errors == []

    def test_missing_ideal_is_rejected_even_at_a_high_score(self) -> None:
        assessment = _valid_assessment()
        assessment["ratings"][0]["ideal"] = ""
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("ideal" in e for e in errors)

    def test_missing_contested_flag_is_rejected(self) -> None:
        assessment = _valid_assessment()
        del assessment["ratings"][0]["contested"]
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("contested" in e for e in errors)


class TestValidateAssessmentComplianceBoundary:
    def test_empty_compliance_is_rejected(self) -> None:
        assessment = _valid_assessment()
        assessment["compliance"] = ""
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("compliance" in e for e in errors)

    def test_cst_vocabulary_in_compliance_is_rejected(self) -> None:
        assessment = _valid_assessment()
        assessment["compliance"] = "In solidarity with data subjects, retention must be bounded."
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("solidarity" in e for e in errors)

    def test_empty_cst_reflection_is_rejected(self) -> None:
        assessment = _valid_assessment()
        assessment["cst_reflection"] = ""
        errors = validate_assessment(
            assessment,
            dimension_ids=DIMENSION_IDS,
            passing_threshold=4,
            framework_records=FRAMEWORK_RECORDS,
        )
        assert any("cst_reflection" in e for e in errors)


class TestLoadAndValidateEndToEnd:
    def test_valid_input_against_the_real_registry_and_rubric(self, tmp_path: Path) -> None:
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(_valid_assessment()))

        assessment, warnings = load_and_validate(
            input_path,
            frameworks_dir=REPO_ROOT / "frameworks",
            rubric_path=REPO_ROOT / "rubric" / "criteria.md",
        )
        assert assessment["title"] == "Parish bulletin sign-up form"
        assert warnings == []

    def test_broken_input_raises_assessment_error_listing_every_problem(
        self, tmp_path: Path
    ) -> None:
        broken = _valid_assessment()
        broken["subject"]["retention"] = ""
        broken["ratings"] = broken["ratings"][:-1]  # drop human-oversight
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(broken))

        with pytest.raises(AssessmentError) as excinfo:
            load_and_validate(
                input_path,
                frameworks_dir=REPO_ROOT / "frameworks",
                rubric_path=REPO_ROOT / "rubric" / "criteria.md",
            )
        assert len(excinfo.value.errors) >= 2
        assert any("retention" in e for e in excinfo.value.errors)
        assert any("human-oversight" in e for e in excinfo.value.errors)
