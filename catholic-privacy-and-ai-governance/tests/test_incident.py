from privacy_and_ai_governance.incident import validate_incident

KNOWN_IDS = {"gdpr-breach-notification", "ca-breach-notification", "hipaa", "ferpa"}


def _valid_incident(**overrides) -> dict:
    incident = {
        "title": "Misdirected email containing parishioner records",
        "incident": {
            "description": "A parish office staff member emailed a spreadsheet of "
            "150 parishioners' names, addresses, and donation history to the wrong "
            "distribution list.",
            "discovered_date": "2026-08-01",
            "affected_systems": ["parish office email", "donor management spreadsheet"],
            "data_types": ["name", "address", "donation history"],
            "individuals_affected_estimate": 150,
        },
        "frameworks_considered": [
            {
                "id": "ca-breach-notification",
                "applicable": True,
                "basis": "Some affected parishioners are California residents.",
            }
        ],
        "severity": {
            "level": "moderate",
            "rationale": "Financial/donation data exposed to an unintended internal "
            "list, not a public or malicious external actor.",
        },
        "notification_obligations": [
            {
                "id": "ca-residents",
                "framework_id": "ca-breach-notification",
                "audience": "Affected California residents",
                "citation": "Civ. Code § 1798.82(a)(2)(A)",
                "due_date": "2026-08-31",
                "basis": "30 calendar days from the 2026-08-01 discovery date, per "
                "Civ. Code § 1798.82(a)(2)(A).",
            }
        ],
        "gaps": [],
        "escalation": {
            "required": True,
            "rationale": "Meets the notification-obligation threshold for "
            "executive/legal awareness even though severity is moderate.",
        },
        "compliance": "Under Civ. Code § 1798.82(a)(2)(A), affected California "
        "residents must be notified within 30 calendar days of the 2026-08-01 "
        "discovery date.",
        "cst_reflection": "Treating the exposure as something owed a prompt, honest "
        "accounting to those affected, not a risk to be managed quietly.",
    }
    incident.update(overrides)
    return incident


class TestValidateIncidentHappyPath:
    def test_a_well_formed_incident_has_no_errors(self) -> None:
        errors = validate_incident(_valid_incident(), known_framework_ids=KNOWN_IDS)
        assert errors == []

    def test_empty_notification_obligations_is_valid(self) -> None:
        # A low-severity incident with no framework triggering notification
        # is a legitimate outcome, not an omission.
        incident = _valid_incident()
        incident["notification_obligations"] = []
        incident["frameworks_considered"] = [
            {"id": "ferpa", "applicable": False, "basis": "No education records involved."}
        ]
        assert validate_incident(incident, known_framework_ids=KNOWN_IDS) == []

    def test_empty_gaps_list_is_valid(self) -> None:
        incident = _valid_incident()
        incident["gaps"] = []
        assert validate_incident(incident, known_framework_ids=KNOWN_IDS) == []


class TestValidateIncidentTopLevel:
    def test_empty_title_is_rejected(self) -> None:
        incident = _valid_incident(title="")
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("title" in e for e in errors)

    def test_empty_compliance_is_rejected(self) -> None:
        incident = _valid_incident(compliance="")
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("compliance" in e for e in errors)

    def test_cst_vocabulary_in_compliance_is_rejected(self) -> None:
        incident = _valid_incident(
            compliance="In solidarity with parishioners, notify them within 30 days."
        )
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("solidarity" in e for e in errors)

    def test_empty_cst_reflection_is_rejected(self) -> None:
        incident = _valid_incident(cst_reflection="")
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("cst_reflection" in e for e in errors)


class TestValidateIncidentFacts:
    def test_missing_description_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["incident"]["description"] = ""
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("description" in e for e in errors)

    def test_invalid_discovered_date_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["incident"]["discovered_date"] = "not-a-date"
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("discovered_date" in e for e in errors)


class TestValidateIncidentFrameworksConsidered:
    def test_empty_frameworks_considered_is_rejected(self) -> None:
        incident = _valid_incident(frameworks_considered=[])
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("frameworks_considered" in e for e in errors)

    def test_unknown_framework_id_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["frameworks_considered"] = [{"id": "made-up", "applicable": True, "basis": "x"}]
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("made-up" in e for e in errors)

    def test_missing_basis_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["frameworks_considered"][0]["basis"] = ""
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("basis" in e for e in errors)

    def test_duplicate_framework_id_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["frameworks_considered"].append(
            {"id": "ca-breach-notification", "applicable": True, "basis": "again"}
        )
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("more than once" in e for e in errors)


class TestValidateIncidentSeverity:
    def test_missing_severity_is_rejected(self) -> None:
        incident = _valid_incident()
        del incident["severity"]
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("severity" in e for e in errors)

    def test_unknown_severity_level_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["severity"]["level"] = "extremely-bad"
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("severity.level" in e for e in errors)

    def test_missing_severity_rationale_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["severity"]["rationale"] = ""
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("severity.rationale" in e for e in errors)

    def test_every_severity_level_is_accepted(self) -> None:
        for level in ("low", "moderate", "high", "critical"):
            incident = _valid_incident()
            incident["severity"]["level"] = level
            assert validate_incident(incident, known_framework_ids=KNOWN_IDS) == []


class TestValidateIncidentNotificationObligations:
    def test_must_reference_a_known_framework(self) -> None:
        incident = _valid_incident()
        incident["notification_obligations"][0]["framework_id"] = "made-up"
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("made-up" in e for e in errors)

    def test_must_reference_an_applicable_framework(self) -> None:
        incident = _valid_incident()
        incident["frameworks_considered"].append(
            {"id": "hipaa", "applicable": False, "basis": "Not a covered entity."}
        )
        incident["notification_obligations"][0]["framework_id"] = "hipaa"
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("hipaa" in e and "applicable" in e for e in errors)

    def test_missing_audience_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["notification_obligations"][0]["audience"] = ""
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("audience" in e for e in errors)

    def test_missing_citation_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["notification_obligations"][0]["citation"] = ""
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("citation" in e for e in errors)

    def test_invalid_due_date_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["notification_obligations"][0]["due_date"] = "not-a-date"
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("due_date" in e for e in errors)

    def test_due_date_before_discovered_date_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["notification_obligations"][0]["due_date"] = "2026-07-01"
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("due_date" in e for e in errors)

    def test_missing_basis_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["notification_obligations"][0]["basis"] = ""
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("basis" in e for e in errors)

    def test_two_independent_obligations_to_different_audiences_are_both_accepted(self) -> None:
        # The whole point of this shape over triage.py's single
        # governing_deadline: multiple simultaneous, non-competing
        # notification duties to different audiences are all real at once.
        incident = _valid_incident()
        incident["frameworks_considered"].append(
            {
                "id": "gdpr-breach-notification",
                "applicable": True,
                "basis": "Some affected parishioners are EU residents.",
            }
        )
        incident["notification_obligations"].append(
            {
                "id": "eu-supervisory-authority",
                "framework_id": "gdpr-breach-notification",
                "audience": "Competent supervisory authority",
                "citation": "Art. 33(1)",
                "due_date": "2026-08-04",
                "basis": "72 hours from the 2026-08-01 discovery, per Art. 33(1).",
            }
        )
        assert validate_incident(incident, known_framework_ids=KNOWN_IDS) == []


class TestValidateIncidentGaps:
    def test_gap_missing_description_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["gaps"] = [{"id": "scope", "description": "", "blocking": True}]
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("description" in e for e in errors)

    def test_gap_missing_blocking_flag_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["gaps"] = [{"id": "scope", "description": "Full scope not yet confirmed."}]
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("blocking" in e for e in errors)


class TestValidateIncidentEscalation:
    def test_missing_escalation_is_rejected(self) -> None:
        incident = _valid_incident()
        del incident["escalation"]
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("escalation" in e for e in errors)

    def test_missing_required_flag_is_rejected(self) -> None:
        incident = _valid_incident()
        del incident["escalation"]["required"]
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("escalation.required" in e for e in errors)

    def test_missing_rationale_is_rejected(self) -> None:
        incident = _valid_incident()
        incident["escalation"]["rationale"] = ""
        errors = validate_incident(incident, known_framework_ids=KNOWN_IDS)
        assert any("escalation.rationale" in e for e in errors)

    def test_escalation_not_required_with_rationale_is_accepted(self) -> None:
        incident = _valid_incident()
        incident["escalation"] = {
            "required": False,
            "rationale": "Low severity, no notification obligation triggered, "
            "contained to internal staff.",
        }
        incident["notification_obligations"] = []
        incident["severity"]["level"] = "low"
        incident["frameworks_considered"] = [
            {"id": "ferpa", "applicable": False, "basis": "No education records involved."}
        ]
        assert validate_incident(incident, known_framework_ids=KNOWN_IDS) == []
