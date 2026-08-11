from privacy_and_ai_governance.concision import lint_assessment, lint_triage


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
