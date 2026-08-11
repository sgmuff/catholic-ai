from privacy_and_ai_governance.regulatory_change import validate_regulatory_change

KNOWN_IDS = {"gdpr-dpia", "ccpa-cpra", "hipaa"}


def _valid_change(**overrides) -> dict:
    change = {
        "title": "CPPA risk-assessment regulations take effect",
        "development": {
            "source": "California Privacy Protection Agency",
            "citation": "Cal. Code Regs. tit. 11, §§ 7150-7157",
            "summary": "New regulations requiring a risk assessment before processing "
            "that presents significant risk to consumers' privacy or security.",
            "published_date": "2026-01-01",
        },
        "frameworks_considered": [
            {
                "id": "ccpa-cpra",
                "impacted": True,
                "basis": "This registry entry already cites Civ. Code § 1798.185(a)(15); "
                "the new regulations flesh out what that risk assessment must contain.",
            }
        ],
        "recommended_actions": [
            {
                "id": "update-risk-assessment-element",
                "type": "update-required-element",
                "framework_id": "ccpa-cpra",
                "description": "Update the risk-assessment required element with the "
                "regulations' specific content requirements.",
            }
        ],
        "compliance": "Under Cal. Code Regs. tit. 11, § 7152, a business must document "
        "specified elements in its risk assessment before conducting the processing.",
        "cst_reflection": "Keeping the registry current is how the assessment a "
        "parishioner's data receives stays honest, not stale.",
    }
    change.update(overrides)
    return change


class TestValidateRegulatoryChangeHappyPath:
    def test_a_well_formed_change_has_no_errors(self) -> None:
        errors = validate_regulatory_change(_valid_change(), known_framework_ids=KNOWN_IDS)
        assert errors == []

    def test_no_action_type_is_valid_with_no_framework_id(self) -> None:
        change = _valid_change()
        change["recommended_actions"] = [
            {
                "id": "no-change-needed",
                "type": "no-action",
                "framework_id": None,
                "description": "Already fully reflected in the current registry entry.",
            }
        ]
        assert validate_regulatory_change(change, known_framework_ids=KNOWN_IDS) == []

    def test_register_new_framework_type_is_valid_with_no_framework_id(self) -> None:
        change = _valid_change()
        change["recommended_actions"] = [
            {
                "id": "register-new-law",
                "type": "register-new-framework",
                "framework_id": None,
                "description": "This is a wholly new statute, not covered by any "
                "registered framework — register it as its own entry.",
            }
        ]
        assert validate_regulatory_change(change, known_framework_ids=KNOWN_IDS) == []


class TestValidateRegulatoryChangeTopLevel:
    def test_empty_title_is_rejected(self) -> None:
        change = _valid_change(title="")
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("title" in e for e in errors)

    def test_empty_compliance_is_rejected(self) -> None:
        change = _valid_change(compliance="")
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("compliance" in e for e in errors)

    def test_cst_vocabulary_in_compliance_is_rejected(self) -> None:
        change = _valid_change(compliance="In solidarity with parishioners, update this.")
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("solidarity" in e for e in errors)

    def test_empty_cst_reflection_is_rejected(self) -> None:
        change = _valid_change(cst_reflection="")
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("cst_reflection" in e for e in errors)


class TestValidateRegulatoryChangeDevelopment:
    def test_missing_source_is_rejected(self) -> None:
        change = _valid_change()
        change["development"]["source"] = ""
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("source" in e for e in errors)

    def test_missing_summary_is_rejected(self) -> None:
        change = _valid_change()
        change["development"]["summary"] = ""
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("summary" in e for e in errors)

    def test_invalid_published_date_is_rejected(self) -> None:
        change = _valid_change()
        change["development"]["published_date"] = "not-a-date"
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("published_date" in e for e in errors)


class TestValidateRegulatoryChangeFrameworksConsidered:
    def test_empty_frameworks_considered_is_rejected(self) -> None:
        change = _valid_change(frameworks_considered=[])
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("frameworks_considered" in e for e in errors)

    def test_unknown_framework_id_is_rejected(self) -> None:
        change = _valid_change()
        change["frameworks_considered"] = [{"id": "made-up", "impacted": True, "basis": "x"}]
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("made-up" in e for e in errors)

    def test_missing_basis_is_rejected(self) -> None:
        change = _valid_change()
        change["frameworks_considered"][0]["basis"] = ""
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("basis" in e for e in errors)


class TestValidateRegulatoryChangeRecommendedActions:
    def test_empty_recommended_actions_is_rejected(self) -> None:
        change = _valid_change(recommended_actions=[])
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("recommended_actions" in e for e in errors)

    def test_unknown_action_type_is_rejected(self) -> None:
        change = _valid_change()
        change["recommended_actions"][0]["type"] = "shrug"
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("type" in e for e in errors)

    def test_missing_description_is_rejected(self) -> None:
        change = _valid_change()
        change["recommended_actions"][0]["description"] = ""
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("description" in e for e in errors)

    def test_update_required_element_without_framework_id_is_rejected(self) -> None:
        change = _valid_change()
        change["recommended_actions"][0]["framework_id"] = None
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("framework_id" in e for e in errors)

    def test_update_required_element_with_unknown_framework_id_is_rejected(self) -> None:
        change = _valid_change()
        change["recommended_actions"][0]["framework_id"] = "made-up"
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("made-up" in e for e in errors)

    def test_retire_framework_without_framework_id_is_rejected(self) -> None:
        change = _valid_change()
        change["recommended_actions"] = [
            {
                "id": "retire-old-law",
                "type": "retire-framework",
                "framework_id": None,
                "description": "This framework has been repealed.",
            }
        ]
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("framework_id" in e for e in errors)

    def test_register_new_framework_with_a_framework_id_is_rejected(self) -> None:
        # A framework_id can't reference something that doesn't exist in the
        # registry yet — that's exactly the case this action type is for.
        change = _valid_change()
        change["recommended_actions"] = [
            {
                "id": "register-new-law",
                "type": "register-new-framework",
                "framework_id": "ccpa-cpra",
                "description": "Should not reference an existing id.",
            }
        ]
        errors = validate_regulatory_change(change, known_framework_ids=KNOWN_IDS)
        assert any("framework_id" in e for e in errors)
