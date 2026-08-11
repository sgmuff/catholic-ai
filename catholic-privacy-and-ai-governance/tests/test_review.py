from privacy_and_ai_governance.review import validate_review

KNOWN_FRAMEWORK_IDS = {"gdpr-dpia", "ccpa-cpra", "hipaa"}
KNOWN_BASELINE_ITEM_IDS = ["dpa-in-place", "sub-processor-disclosure", "security-controls-evidence"]


def _valid_review(**overrides) -> dict:
    review = {
        "title": "Annual review of MailerParish, Inc.",
        "vendor": {
            "name": "MailerParish, Inc.",
            "description": "A bulk-email vendor the parish office uses to send the "
            "weekly bulletin to subscribed parishioners.",
            "service_provided": "Bulk email delivery and subscriber list hosting.",
        },
        "frameworks_considered": [
            {
                "id": "gdpr-dpia",
                "applicable": True,
                "basis": "Some subscribed parishioners are EU residents.",
            }
        ],
        "baseline_items": [
            {
                "id": "dpa-in-place",
                "status": "satisfied",
                "evidence": "Signed DPA on file, executed 2025-01-10, Section 4 covers "
                "subject matter and duration of processing.",
                "gap": None,
            },
            {
                "id": "sub-processor-disclosure",
                "status": "partial",
                "evidence": "Vendor's public sub-processor list page is referenced in the DPA.",
                "gap": "The DPA references the page but doesn't require advance notice "
                "before a new sub-processor is added.",
            },
            {
                "id": "security-controls-evidence",
                "status": "missing",
                "evidence": None,
                "gap": "No current SOC 2 report or completed security questionnaire on "
                "file; the one provided at signup has expired.",
            },
        ],
        "remediation_commitments": [
            {
                "id": "security-questionnaire",
                "description": "Vendor to provide an updated security questionnaire.",
                "target_date": "2026-09-15",
                "status": "open",
            }
        ],
        "reassessment_due": "2027-08-01",
        "overall_risk": {
            "level": "moderate",
            "rationale": "One baseline item unmet and one partial, but the vendor is "
            "responsive and has an open remediation commitment with a near-term date.",
        },
        "compliance": "Under GDPR Art. 28(3), the processing terms must specify the "
        "subject matter and duration of processing; the current DPA satisfies this, but "
        "current security-control evidence is required before the relationship "
        "continues past the remediation date.",
        "cst_reflection": "The parishioners on this list trusted the parish with their "
        "contact information, not this vendor directly; closing the security-evidence "
        "gap keeps that trust intact rather than delegating it away unexamined.",
    }
    review.update(overrides)
    return review


class TestValidateReviewHappyPath:
    def test_a_well_formed_review_has_no_errors(self) -> None:
        errors = validate_review(
            _valid_review(),
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert errors == []

    def test_empty_remediation_commitments_is_valid(self) -> None:
        review = _valid_review()
        review["remediation_commitments"] = []
        review["baseline_items"] = [
            {"id": "dpa-in-place", "status": "satisfied", "evidence": "On file.", "gap": None},
            {
                "id": "sub-processor-disclosure",
                "status": "satisfied",
                "evidence": "Disclosed in DPA Annex 2.",
                "gap": None,
            },
            {
                "id": "security-controls-evidence",
                "status": "satisfied",
                "evidence": "Current SOC 2 Type II report on file.",
                "gap": None,
            },
        ]
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert errors == []


class TestValidateReviewTopLevel:
    def test_empty_title_is_rejected(self) -> None:
        review = _valid_review(title="")
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("title" in e for e in errors)

    def test_empty_compliance_is_rejected(self) -> None:
        review = _valid_review(compliance="")
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("compliance" in e for e in errors)

    def test_cst_vocabulary_in_compliance_is_rejected(self) -> None:
        review = _valid_review(compliance="In solidarity with parishioners, close this gap.")
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("solidarity" in e for e in errors)

    def test_empty_cst_reflection_is_rejected(self) -> None:
        review = _valid_review(cst_reflection="")
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("cst_reflection" in e for e in errors)


class TestValidateReviewVendor:
    def test_missing_vendor_name_is_rejected(self) -> None:
        review = _valid_review()
        review["vendor"]["name"] = ""
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("vendor.name" in e for e in errors)

    def test_missing_vendor_description_is_rejected(self) -> None:
        review = _valid_review()
        review["vendor"]["description"] = ""
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("vendor.description" in e for e in errors)


class TestValidateReviewFrameworksConsidered:
    def test_empty_frameworks_considered_is_rejected(self) -> None:
        review = _valid_review(frameworks_considered=[])
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("frameworks_considered" in e for e in errors)

    def test_unknown_framework_id_is_rejected(self) -> None:
        review = _valid_review()
        review["frameworks_considered"] = [{"id": "made-up", "applicable": True, "basis": "x"}]
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("made-up" in e for e in errors)


class TestValidateReviewBaselineItems:
    def test_missing_baseline_item_is_rejected(self) -> None:
        review = _valid_review()
        review["baseline_items"] = review["baseline_items"][:2]
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("security-controls-evidence" in e for e in errors)

    def test_unknown_baseline_item_is_rejected(self) -> None:
        review = _valid_review()
        review["baseline_items"].append(
            {"id": "made-up-item", "status": "satisfied", "evidence": "x", "gap": None}
        )
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("made-up-item" in e for e in errors)

    def test_duplicate_baseline_item_is_rejected(self) -> None:
        review = _valid_review()
        review["baseline_items"].append(dict(review["baseline_items"][0]))
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("dpa-in-place" in e and "more than once" in e for e in errors)

    def test_invalid_status_is_rejected(self) -> None:
        review = _valid_review()
        review["baseline_items"][0]["status"] = "sort-of"
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("status" in e for e in errors)

    def test_satisfied_without_evidence_is_rejected(self) -> None:
        review = _valid_review()
        review["baseline_items"][0]["evidence"] = None
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("evidence" in e for e in errors)

    def test_partial_without_gap_is_rejected(self) -> None:
        review = _valid_review()
        review["baseline_items"][1]["gap"] = None
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("gap" in e for e in errors)

    def test_missing_without_gap_is_rejected(self) -> None:
        review = _valid_review()
        review["baseline_items"][2]["gap"] = None
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("gap" in e for e in errors)


class TestValidateReviewRemediationCommitments:
    def test_missing_description_is_rejected(self) -> None:
        review = _valid_review()
        review["remediation_commitments"][0]["description"] = ""
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("description" in e for e in errors)

    def test_invalid_target_date_is_rejected(self) -> None:
        review = _valid_review()
        review["remediation_commitments"][0]["target_date"] = "not-a-date"
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("target_date" in e for e in errors)

    def test_invalid_status_is_rejected(self) -> None:
        review = _valid_review()
        review["remediation_commitments"][0]["status"] = "done-ish"
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("status" in e for e in errors)


class TestValidateReviewReassessmentAndRisk:
    def test_invalid_reassessment_due_is_rejected(self) -> None:
        review = _valid_review(reassessment_due="not-a-date")
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("reassessment_due" in e for e in errors)

    def test_missing_overall_risk_is_rejected(self) -> None:
        review = _valid_review()
        del review["overall_risk"]
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("overall_risk" in e for e in errors)

    def test_unknown_risk_level_is_rejected(self) -> None:
        review = _valid_review()
        review["overall_risk"]["level"] = "super-bad"
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("overall_risk.level" in e for e in errors)

    def test_missing_risk_rationale_is_rejected(self) -> None:
        review = _valid_review()
        review["overall_risk"]["rationale"] = ""
        errors = validate_review(
            review,
            known_framework_ids=KNOWN_FRAMEWORK_IDS,
            known_baseline_item_ids=KNOWN_BASELINE_ITEM_IDS,
        )
        assert any("overall_risk.rationale" in e for e in errors)
