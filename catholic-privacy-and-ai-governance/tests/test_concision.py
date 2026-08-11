from privacy_and_ai_governance.concision import (
    lint_assessment,
    lint_incident,
    lint_review,
    lint_triage,
)


def _tight_rating(dimension_id: str = "retention") -> dict:
    return {
        "dimension_id": dimension_id,
        "score": 5,
        "rationale": "Retention is capped at 90 days and enforced by a scheduled job.",
        "mitigation": None,
        "ideal": "Already at the floor and the ceiling here.",
        "contested": False,
    }


def _tight_assessment() -> dict:
    return {
        "ratings": [_tight_rating()],
        "frameworks_considered": [{"id": "gdpr-dpia", "applicable": True}],
        "compliance": "Under GDPR Art. 35(7)(d), retention is bounded and enforced.",
        "cst_reflection": "This keeps the data no longer than the relationship it serves.",
    }


class TestLintAssessment:
    def test_tight_assessment_produces_no_warnings(self) -> None:
        assert lint_assessment(_tight_assessment()) == []

    def test_does_not_raise_on_a_padded_assessment(self) -> None:
        # non-fatal by design — this must never throw, only warn
        padded = _tight_assessment()
        padded["compliance"] = "word " * 5000
        lint_assessment(padded)  # should not raise

    def test_flags_an_overlong_rating_field(self) -> None:
        assessment = _tight_assessment()
        assessment["ratings"][0]["rationale"] = "word " * 500
        warnings = lint_assessment(assessment)
        assert any("retention" in w and "rationale" in w for w in warnings)

    def test_flags_compliance_section_long_relative_to_applicable_scope(self) -> None:
        assessment = _tight_assessment()
        assessment["frameworks_considered"] = [{"id": "gdpr-dpia", "applicable": True}]
        assessment["compliance"] = "word " * 2000
        warnings = lint_assessment(assessment)
        assert any("compliance" in w for w in warnings)

    def test_more_applicable_frameworks_raises_the_compliance_allowance(self) -> None:
        few = _tight_assessment()
        few["frameworks_considered"] = [{"id": "gdpr-dpia", "applicable": True}]
        few["compliance"] = "word " * 300

        many = _tight_assessment()
        many["frameworks_considered"] = [
            {"id": "gdpr-dpia", "applicable": True},
            {"id": "ccpa-cpra", "applicable": True},
            {"id": "hipaa", "applicable": True},
        ]
        many["compliance"] = "word " * 300

        few_warnings = lint_assessment(few)
        many_warnings = lint_assessment(many)
        assert any("compliance" in w for w in few_warnings)
        assert not any("compliance" in w for w in many_warnings)

    def test_flags_overlong_cst_reflection(self) -> None:
        assessment = _tight_assessment()
        assessment["cst_reflection"] = "word " * 1000
        warnings = lint_assessment(assessment)
        assert any("cst_reflection" in w for w in warnings)

    def test_non_applicable_frameworks_do_not_count_toward_allowance(self) -> None:
        assessment = _tight_assessment()
        assessment["frameworks_considered"] = [
            {"id": "gdpr-dpia", "applicable": True},
            {"id": "hipaa", "applicable": False},
            {"id": "ferpa", "applicable": False},
        ]
        assessment["compliance"] = "word " * 300
        warnings = lint_assessment(assessment)
        assert any("compliance" in w for w in warnings)


def _tight_triage() -> dict:
    return {
        "title": "Access request",
        "request": {
            "description": "A parishioner asked for a copy of their data.",
            "request_type": "access",
        },
        "frameworks_considered": [{"id": "gdpr-data-subject-rights", "applicable": True}],
        "governing_deadline": {
            "framework_id": "gdpr-data-subject-rights",
            "citation": "Art. 12(3)",
            "response_due": "2026-09-01",
            "basis": "One month from receipt, per Art. 12(3).",
        },
        "gaps": [{"id": "identity", "description": "Identity not yet verified.", "blocking": True}],
        "compliance": "Under Art. 15, a copy of the data held must be provided within "
        "the Art. 12(3) deadline above.",
        "cst_reflection": "Responding promptly treats the request as owed, not optional.",
    }


class TestLintTriage:
    def test_tight_triage_produces_no_warnings(self) -> None:
        assert lint_triage(_tight_triage()) == []

    def test_does_not_raise_on_a_padded_triage(self) -> None:
        padded = _tight_triage()
        padded["compliance"] = "word " * 5000
        lint_triage(padded)  # should not raise

    def test_flags_overlong_request_description(self) -> None:
        triage = _tight_triage()
        triage["request"]["description"] = "word " * 500
        warnings = lint_triage(triage)
        assert any("request.description" in w for w in warnings)

    def test_flags_overlong_gap_description(self) -> None:
        triage = _tight_triage()
        triage["gaps"][0]["description"] = "word " * 500
        warnings = lint_triage(triage)
        assert any("gaps[identity]" in w for w in warnings)

    def test_flags_overlong_deadline_basis(self) -> None:
        triage = _tight_triage()
        triage["governing_deadline"]["basis"] = "word " * 500
        warnings = lint_triage(triage)
        assert any("governing_deadline.basis" in w for w in warnings)

    def test_flags_overlong_compliance_relative_to_applicable_scope(self) -> None:
        triage = _tight_triage()
        triage["compliance"] = "word " * 2000
        warnings = lint_triage(triage)
        assert any("compliance" in w for w in warnings)

    def test_flags_overlong_cst_reflection(self) -> None:
        triage = _tight_triage()
        triage["cst_reflection"] = "word " * 1000
        warnings = lint_triage(triage)
        assert any("cst_reflection" in w for w in warnings)


def _tight_incident() -> dict:
    return {
        "title": "Misdirected email",
        "incident": {
            "description": "A staff member emailed a donor list to the wrong address.",
        },
        "frameworks_considered": [{"id": "ca-breach-notification", "applicable": True}],
        "notification_obligations": [
            {
                "id": "ca-residents",
                "basis": "30 days from discovery, per Civ. Code § 1798.82(a)(2)(A).",
            }
        ],
        "gaps": [{"id": "scope", "description": "Full scope not yet confirmed."}],
        "compliance": "Under Civ. Code § 1798.82, affected residents must be notified "
        "within 30 calendar days.",
        "cst_reflection": "Treating the exposure as owed a prompt, honest accounting.",
    }


class TestLintIncident:
    def test_tight_incident_produces_no_warnings(self) -> None:
        assert lint_incident(_tight_incident()) == []

    def test_does_not_raise_on_a_padded_incident(self) -> None:
        padded = _tight_incident()
        padded["compliance"] = "word " * 5000
        lint_incident(padded)  # should not raise

    def test_flags_overlong_incident_description(self) -> None:
        incident = _tight_incident()
        incident["incident"]["description"] = "word " * 500
        warnings = lint_incident(incident)
        assert any("incident.description" in w for w in warnings)

    def test_flags_overlong_gap_description(self) -> None:
        incident = _tight_incident()
        incident["gaps"][0]["description"] = "word " * 500
        warnings = lint_incident(incident)
        assert any("gaps[scope]" in w for w in warnings)

    def test_flags_overlong_notification_obligation_basis(self) -> None:
        incident = _tight_incident()
        incident["notification_obligations"][0]["basis"] = "word " * 500
        warnings = lint_incident(incident)
        assert any("notification_obligations[ca-residents]" in w for w in warnings)

    def test_flags_overlong_compliance_relative_to_applicable_scope(self) -> None:
        incident = _tight_incident()
        incident["compliance"] = "word " * 2000
        warnings = lint_incident(incident)
        assert any("compliance" in w for w in warnings)

    def test_flags_overlong_cst_reflection(self) -> None:
        incident = _tight_incident()
        incident["cst_reflection"] = "word " * 1000
        warnings = lint_incident(incident)
        assert any("cst_reflection" in w for w in warnings)


def _tight_review() -> dict:
    return {
        "title": "Annual review of MailerParish, Inc.",
        "vendor": {"description": "A bulk-email vendor used to send the weekly bulletin."},
        "frameworks_considered": [{"id": "gdpr-dpia", "applicable": True}],
        "baseline_items": [
            {"id": "dpa-in-place", "evidence": "Signed DPA on file.", "gap": None},
            {
                "id": "security-controls-evidence",
                "evidence": None,
                "gap": "No current SOC 2 report on file.",
            },
        ],
        "remediation_commitments": [
            {"id": "security-questionnaire", "description": "Provide an updated questionnaire."}
        ],
        "overall_risk": {"rationale": "One item unmet, with an open remediation commitment."},
        "compliance": "Under GDPR Art. 28(3), the DPA must specify processing terms.",
        "cst_reflection": "Closing this gap keeps the parishioners' trust intact.",
    }


class TestLintReview:
    def test_tight_review_produces_no_warnings(self) -> None:
        assert lint_review(_tight_review()) == []

    def test_does_not_raise_on_a_padded_review(self) -> None:
        padded = _tight_review()
        padded["compliance"] = "word " * 5000
        lint_review(padded)  # should not raise

    def test_flags_overlong_vendor_description(self) -> None:
        review = _tight_review()
        review["vendor"]["description"] = "word " * 500
        warnings = lint_review(review)
        assert any("vendor.description" in w for w in warnings)

    def test_flags_overlong_baseline_item_evidence(self) -> None:
        review = _tight_review()
        review["baseline_items"][0]["evidence"] = "word " * 500
        warnings = lint_review(review)
        assert any("baseline_items[dpa-in-place].evidence" in w for w in warnings)

    def test_flags_overlong_baseline_item_gap(self) -> None:
        review = _tight_review()
        review["baseline_items"][1]["gap"] = "word " * 500
        warnings = lint_review(review)
        assert any("baseline_items[security-controls-evidence].gap" in w for w in warnings)

    def test_flags_overlong_remediation_commitment_description(self) -> None:
        review = _tight_review()
        review["remediation_commitments"][0]["description"] = "word " * 500
        warnings = lint_review(review)
        assert any("remediation_commitments[security-questionnaire]" in w for w in warnings)

    def test_flags_overlong_overall_risk_rationale(self) -> None:
        review = _tight_review()
        review["overall_risk"]["rationale"] = "word " * 500
        warnings = lint_review(review)
        assert any("overall_risk.rationale" in w for w in warnings)

    def test_flags_overlong_compliance_relative_to_applicable_scope(self) -> None:
        review = _tight_review()
        review["compliance"] = "word " * 2000
        warnings = lint_review(review)
        assert any("compliance" in w for w in warnings)

    def test_flags_overlong_cst_reflection(self) -> None:
        review = _tight_review()
        review["cst_reflection"] = "word " * 1000
        warnings = lint_review(review)
        assert any("cst_reflection" in w for w in warnings)
