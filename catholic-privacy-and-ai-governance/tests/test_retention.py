from privacy_and_ai_governance.retention import validate_retention_entry

KNOWN_IDS = {"gdpr-dpia", "ccpa-cpra", "hipaa"}


def _valid_entry(**overrides) -> dict:
    entry = {
        "title": "Parish bulletin subscriber list",
        "entry": {
            "description": "Email addresses and names collected via the bulletin sign-up form.",
            "category": "data element",
            "purpose": "Sending the weekly parish bulletin.",
            "last_reviewed_date": "2025-08-01",
        },
        "frameworks_considered": [
            {
                "id": "gdpr-dpia",
                "applicable": True,
                "basis": "Some subscribers are EU residents.",
            }
        ],
        "verdict": {
            "action": "needs-review",
            "rationale": "No re-confirmation has happened in over a year despite the "
            "stated annual review policy.",
            "target_date": "2026-09-01",
        },
        "compliance": "Under GDPR Art. 5(1)(e), personal data must not be kept longer "
        "than necessary; the entry is overdue for its own stated annual review.",
        "cst_reflection": "Letting a review lapse quietly treats indefinite retention "
        "as the default, when the parishioner's data is owed an active justification.",
    }
    entry.update(overrides)
    return entry


class TestValidateRetentionEntryHappyPath:
    def test_a_well_formed_entry_has_no_errors(self) -> None:
        errors = validate_retention_entry(_valid_entry(), known_framework_ids=KNOWN_IDS)
        assert errors == []

    def test_current_action_does_not_require_a_target_date(self) -> None:
        entry = _valid_entry()
        entry["verdict"] = {
            "action": "current",
            "rationale": "Reviewed six months ago and retention remains justified.",
            "target_date": None,
        }
        assert validate_retention_entry(entry, known_framework_ids=KNOWN_IDS) == []


class TestValidateRetentionEntryTopLevel:
    def test_empty_title_is_rejected(self) -> None:
        entry = _valid_entry(title="")
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("title" in e for e in errors)

    def test_empty_compliance_is_rejected(self) -> None:
        entry = _valid_entry(compliance="")
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("compliance" in e for e in errors)

    def test_cst_vocabulary_in_compliance_is_rejected(self) -> None:
        entry = _valid_entry(compliance="In solidarity with parishioners, review this now.")
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("solidarity" in e for e in errors)

    def test_empty_cst_reflection_is_rejected(self) -> None:
        entry = _valid_entry(cst_reflection="")
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("cst_reflection" in e for e in errors)


class TestValidateRetentionEntryFacts:
    def test_missing_description_is_rejected(self) -> None:
        entry = _valid_entry()
        entry["entry"]["description"] = ""
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("description" in e for e in errors)

    def test_missing_category_is_rejected(self) -> None:
        entry = _valid_entry()
        entry["entry"]["category"] = ""
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("category" in e for e in errors)

    def test_missing_purpose_is_rejected(self) -> None:
        entry = _valid_entry()
        entry["entry"]["purpose"] = ""
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("purpose" in e for e in errors)

    def test_invalid_last_reviewed_date_is_rejected(self) -> None:
        entry = _valid_entry()
        entry["entry"]["last_reviewed_date"] = "not-a-date"
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("last_reviewed_date" in e for e in errors)


class TestValidateRetentionEntryFrameworksConsidered:
    def test_empty_frameworks_considered_is_rejected(self) -> None:
        entry = _valid_entry(frameworks_considered=[])
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("frameworks_considered" in e for e in errors)

    def test_unknown_framework_id_is_rejected(self) -> None:
        entry = _valid_entry()
        entry["frameworks_considered"] = [{"id": "made-up", "applicable": True, "basis": "x"}]
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("made-up" in e for e in errors)


class TestValidateRetentionEntryVerdict:
    def test_missing_verdict_is_rejected(self) -> None:
        entry = _valid_entry()
        del entry["verdict"]
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("verdict" in e for e in errors)

    def test_unknown_action_is_rejected(self) -> None:
        entry = _valid_entry()
        entry["verdict"]["action"] = "shred-it"
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("verdict.action" in e for e in errors)

    def test_missing_rationale_is_rejected(self) -> None:
        entry = _valid_entry()
        entry["verdict"]["rationale"] = ""
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("verdict.rationale" in e for e in errors)

    def test_needs_review_without_target_date_is_rejected(self) -> None:
        entry = _valid_entry()
        entry["verdict"]["target_date"] = None
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("target_date" in e for e in errors)

    def test_invalid_target_date_is_rejected(self) -> None:
        entry = _valid_entry()
        entry["verdict"]["target_date"] = "not-a-date"
        errors = validate_retention_entry(entry, known_framework_ids=KNOWN_IDS)
        assert any("target_date" in e for e in errors)

    def test_every_action_value_is_accepted_with_the_right_target_date_state(self) -> None:
        for action in ("needs-review", "needs-update", "retire"):
            entry = _valid_entry()
            entry["verdict"] = {
                "action": action,
                "rationale": f"A grounded rationale for {action}.",
                "target_date": "2026-09-01",
            }
            assert validate_retention_entry(entry, known_framework_ids=KNOWN_IDS) == []
