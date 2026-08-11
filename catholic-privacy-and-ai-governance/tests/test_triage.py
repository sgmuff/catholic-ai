from privacy_and_ai_governance.triage import validate_triage

KNOWN_IDS = {"gdpr-data-subject-rights", "ccpa-cpra", "hipaa"}


def _valid_triage(**overrides) -> dict:
    triage = {
        "title": "Access request from a returning parishioner",
        "request": {
            "description": "A parishioner emailed asking for a copy of all data the "
            "parish holds about them.",
            "request_type": "access",
            "channel": "email",
            "received_date": "2026-08-01",
            "requester_context": "The data subject themselves.",
        },
        "frameworks_considered": [
            {
                "id": "gdpr-data-subject-rights",
                "applicable": True,
                "basis": "The parishioner is an EU resident.",
            }
        ],
        "governing_deadline": {
            "framework_id": "gdpr-data-subject-rights",
            "citation": "Art. 12(3)",
            "response_due": "2026-09-01",
            "basis": "One month from the 2026-08-01 receipt date, per Art. 12(3).",
        },
        "gaps": [],
        "compliance": "Under Art. 15, the parish must provide confirmation of "
        "processing and a copy of the personal data held, within the Art. 12(3) "
        "deadline above.",
        "cst_reflection": "Responding promptly and completely treats the "
        "parishioner's request as something owed to them, not a formality to "
        "satisfy at the last possible moment.",
    }
    triage.update(overrides)
    return triage


class TestValidateTriageHappyPath:
    def test_a_well_formed_triage_has_no_errors(self) -> None:
        errors = validate_triage(_valid_triage(), known_framework_ids=KNOWN_IDS)
        assert errors == []

    def test_an_empty_gaps_list_is_valid(self) -> None:
        # Unlike frameworks_considered, an empty gaps list is a legitimate
        # "we have everything we need" state, not an omission.
        triage = _valid_triage()
        triage["gaps"] = []
        assert validate_triage(triage, known_framework_ids=KNOWN_IDS) == []


class TestValidateTriageTopLevel:
    def test_empty_title_is_rejected(self) -> None:
        triage = _valid_triage(title="")
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("title" in e for e in errors)

    def test_empty_compliance_is_rejected(self) -> None:
        triage = _valid_triage(compliance="")
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("compliance" in e for e in errors)

    def test_cst_vocabulary_in_compliance_is_rejected(self) -> None:
        triage = _valid_triage(compliance="In solidarity with the parishioner, respond promptly.")
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("solidarity" in e for e in errors)

    def test_empty_cst_reflection_is_rejected(self) -> None:
        triage = _valid_triage(cst_reflection="")
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("cst_reflection" in e for e in errors)


class TestValidateTriageRequest:
    def test_missing_request_type_is_rejected(self) -> None:
        triage = _valid_triage()
        del triage["request"]["request_type"]
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("request_type" in e for e in errors)

    def test_missing_description_is_rejected(self) -> None:
        triage = _valid_triage()
        triage["request"]["description"] = ""
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("description" in e for e in errors)

    def test_invalid_received_date_is_rejected(self) -> None:
        triage = _valid_triage()
        triage["request"]["received_date"] = "not-a-date"
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("received_date" in e for e in errors)


class TestValidateTriageFrameworksConsidered:
    def test_empty_frameworks_considered_is_rejected(self) -> None:
        triage = _valid_triage(frameworks_considered=[])
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("frameworks_considered" in e for e in errors)

    def test_unknown_framework_id_is_rejected(self) -> None:
        triage = _valid_triage()
        triage["frameworks_considered"] = [{"id": "made-up", "applicable": True, "basis": "x"}]
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("made-up" in e for e in errors)

    def test_missing_basis_is_rejected(self) -> None:
        triage = _valid_triage()
        triage["frameworks_considered"][0]["basis"] = ""
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("basis" in e for e in errors)


class TestValidateTriageGoverningDeadline:
    def test_missing_governing_deadline_is_rejected(self) -> None:
        triage = _valid_triage()
        del triage["governing_deadline"]
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("governing_deadline" in e for e in errors)

    def test_governing_deadline_must_reference_a_known_framework(self) -> None:
        triage = _valid_triage()
        triage["governing_deadline"]["framework_id"] = "made-up"
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("made-up" in e for e in errors)

    def test_governing_deadline_must_reference_an_applicable_framework(self) -> None:
        # The governing deadline can't come from a framework that was ruled
        # inapplicable — a real cross-field consistency check this shape
        # needs that the rubric-scored shape never did.
        triage = _valid_triage()
        triage["frameworks_considered"].append(
            {"id": "hipaa", "applicable": False, "basis": "Not a covered entity."}
        )
        triage["governing_deadline"]["framework_id"] = "hipaa"
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("hipaa" in e and "applicable" in e for e in errors)

    def test_invalid_response_due_date_is_rejected(self) -> None:
        triage = _valid_triage()
        triage["governing_deadline"]["response_due"] = "not-a-date"
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("response_due" in e for e in errors)

    def test_response_due_before_received_date_is_rejected(self) -> None:
        triage = _valid_triage()
        triage["governing_deadline"]["response_due"] = "2026-07-01"  # before received_date
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("response_due" in e for e in errors)

    def test_missing_deadline_basis_is_rejected(self) -> None:
        triage = _valid_triage()
        triage["governing_deadline"]["basis"] = ""
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("basis" in e for e in errors)


class TestValidateTriageGaps:
    def test_gap_missing_description_is_rejected(self) -> None:
        triage = _valid_triage()
        triage["gaps"] = [{"id": "identity", "description": "", "blocking": True}]
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("description" in e for e in errors)

    def test_gap_missing_blocking_flag_is_rejected(self) -> None:
        triage = _valid_triage()
        triage["gaps"] = [{"id": "identity", "description": "Identity not yet verified."}]
        errors = validate_triage(triage, known_framework_ids=KNOWN_IDS)
        assert any("blocking" in e for e in errors)

    def test_a_well_formed_gap_is_accepted(self) -> None:
        triage = _valid_triage()
        triage["gaps"] = [
            {"id": "identity", "description": "Identity not yet verified.", "blocking": True}
        ]
        assert validate_triage(triage, known_framework_ids=KNOWN_IDS) == []
