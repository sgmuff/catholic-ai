import datetime
from pathlib import Path

from privacy_and_ai_governance.report import (
    render_incident_markdown,
    render_markdown,
    render_regulatory_change_markdown,
    render_retention_markdown,
    render_review_markdown,
    render_triage_markdown,
    slugify,
    write_report,
)


def _assessment() -> dict:
    return {
        "title": "Parish Bulletin Sign-Up Form",
        "subject": {
            "description": "A web form collecting email addresses for a weekly bulletin.",
            "personal_data": ["email address", "first name"],
            "purpose": "Sending the weekly parish bulletin.",
            "systems": ["Mailchimp"],
            "recipients": ["parish office staff", "Mailchimp (processor)"],
            "retention": "Kept until the parishioner unsubscribes.",
            "institution_context": "A parish",
        },
        "frameworks_considered": [
            {
                "id": "gdpr-dpia",
                "applicable": True,
                "basis": "Parish serves EU-resident parishioners.",
            }
        ],
        "ratings": [
            {
                "dimension_id": "retention",
                "score": 3,
                "rationale": "No automated deletion trigger beyond unsubscribe.",
                "mitigation": "Add an annual re-confirmation with automatic removal on non-response.",
                "ideal": "A defined retention window enforced by a scheduled job.",
                "contested": False,
            },
            {
                "dimension_id": "human-oversight",
                "score": 5,
                "rationale": "No automated decision-making is involved in this activity.",
                "mitigation": None,
                "ideal": "Already at the ceiling — no automated decision exists to oversee.",
                "contested": False,
            },
        ],
        "compliance": "Under GDPR Art. 35(7)(d), retention must be bounded and enforced.",
        "cst_reflection": "This keeps the parishioner's data tied to an active relationship.",
    }


class TestRenderMarkdown:
    def test_renders_the_title_as_a_heading(self) -> None:
        markdown = render_markdown(_assessment())
        assert markdown.startswith("# Parish Bulletin Sign-Up Form")

    def test_cst_summary_precedes_compliance_section(self) -> None:
        # render_markdown is the one shape where this leads, per
        # build-plan.md §2.1's amendment (build sequence step 20) — every
        # other renderer in this module still puts compliance first.
        markdown = render_markdown(_assessment())
        cst_index = markdown.index("## Catholic Social Teaching summary")
        compliance_index = markdown.index("## Compliance")
        assert cst_index < compliance_index

    def test_compliance_text_is_included_verbatim(self) -> None:
        markdown = render_markdown(_assessment())
        assert "Under GDPR Art. 35(7)(d), retention must be bounded and enforced." in markdown

    def test_cst_reflection_text_is_included_verbatim(self) -> None:
        markdown = render_markdown(_assessment())
        assert "This keeps the parishioner's data tied to an active relationship." in markdown

    def test_every_rating_appears_with_its_score(self) -> None:
        markdown = render_markdown(_assessment())
        assert "retention" in markdown
        assert "3/5" in markdown
        assert "human-oversight" in markdown
        assert "5/5" in markdown

    def test_mitigation_appears_only_when_present(self) -> None:
        markdown = render_markdown(_assessment())
        assert "Add an annual re-confirmation" in markdown

    def test_advisory_disclosure_is_present(self) -> None:
        # Deliberately generic — not "DPO" or another privacy-specific title
        # — since report.py is shared, byte-for-byte, across every domain's
        # skills (build sequence step 11 made this explicit).
        markdown = render_markdown(_assessment())
        assert "not a legal opinion" in markdown
        assert "accountable person" in markdown


def _triage() -> dict:
    return {
        "title": "Access request from a returning parishioner",
        "request": {
            "description": "A parishioner emailed asking for a copy of all data held.",
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
        "gaps": [
            {
                "id": "identity",
                "description": "Identity not yet verified against parish records.",
                "blocking": True,
            }
        ],
        "compliance": "Under Art. 15, the parish must provide confirmation of "
        "processing and a copy of the personal data held.",
        "cst_reflection": "Responding promptly treats the request as owed, not optional.",
    }


class TestRenderTriageMarkdown:
    def test_renders_the_title_as_a_heading(self) -> None:
        markdown = render_triage_markdown(_triage())
        assert markdown.startswith("# Access request from a returning parishioner")

    def test_compliance_section_precedes_cst_reflection(self) -> None:
        markdown = render_triage_markdown(_triage())
        compliance_index = markdown.index("## Compliance")
        cst_index = markdown.index("## Catholic Social Teaching reflection")
        assert compliance_index < cst_index

    def test_governing_deadline_is_prominently_rendered(self) -> None:
        markdown = render_triage_markdown(_triage())
        assert "2026-09-01" in markdown
        assert "Art. 12(3)" in markdown

    def test_blocking_gap_is_rendered(self) -> None:
        markdown = render_triage_markdown(_triage())
        assert "Identity not yet verified against parish records." in markdown

    def test_no_gaps_renders_a_clean_statement_not_an_empty_section(self) -> None:
        triage = _triage()
        triage["gaps"] = []
        markdown = render_triage_markdown(triage)
        assert "no outstanding" in markdown.lower() or "none identified" in markdown.lower()

    def test_advisory_disclosure_is_present(self) -> None:
        markdown = render_triage_markdown(_triage())
        assert "not a legal opinion" in markdown
        assert "accountable person" in markdown


def _incident() -> dict:
    return {
        "title": "Misdirected email containing parishioner records",
        "incident": {
            "description": "A parish office staff member emailed a spreadsheet of "
            "150 parishioners' donation history to the wrong distribution list.",
            "discovered_date": "2026-08-01",
            "affected_systems": ["parish office email"],
            "data_types": ["name", "donation history"],
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
            "rationale": "Financial data exposed internally, not to a malicious actor.",
        },
        "notification_obligations": [
            {
                "id": "ca-residents",
                "framework_id": "ca-breach-notification",
                "audience": "Affected California residents",
                "citation": "Civ. Code § 1798.82(a)(2)(A)",
                "due_date": "2026-08-31",
                "basis": "30 calendar days from the 2026-08-01 discovery date.",
            }
        ],
        "gaps": [
            {
                "id": "scope",
                "description": "Full list of affected recipients not yet confirmed.",
                "blocking": True,
            }
        ],
        "escalation": {
            "required": True,
            "rationale": "Meets the notification-obligation threshold.",
        },
        "compliance": "Under Civ. Code § 1798.82(a)(2)(A), affected California "
        "residents must be notified within 30 calendar days of discovery.",
        "cst_reflection": "Treating the exposure as owed a prompt, honest accounting.",
    }


class TestRenderIncidentMarkdown:
    def test_renders_the_title_as_a_heading(self) -> None:
        markdown = render_incident_markdown(_incident())
        assert markdown.startswith("# Misdirected email containing parishioner records")

    def test_compliance_section_precedes_cst_reflection(self) -> None:
        markdown = render_incident_markdown(_incident())
        compliance_index = markdown.index("## Compliance")
        cst_index = markdown.index("## Catholic Social Teaching reflection")
        assert compliance_index < cst_index

    def test_severity_is_rendered(self) -> None:
        markdown = render_incident_markdown(_incident())
        assert "moderate" in markdown.lower()

    def test_every_notification_obligation_appears_with_its_audience_and_due_date(self) -> None:
        markdown = render_incident_markdown(_incident())
        assert "Affected California residents" in markdown
        assert "2026-08-31" in markdown
        assert "Civ. Code § 1798.82(a)(2)(A)" in markdown

    def test_multiple_notification_obligations_all_appear(self) -> None:
        incident = _incident()
        incident["frameworks_considered"].append(
            {
                "id": "gdpr-breach-notification",
                "applicable": True,
                "basis": "Some affected parishioners are EU residents.",
            }
        )
        incident["notification_obligations"].append(
            {
                "id": "eu-authority",
                "framework_id": "gdpr-breach-notification",
                "audience": "Competent supervisory authority",
                "citation": "Art. 33(1)",
                "due_date": "2026-08-04",
                "basis": "72 hours from discovery.",
            }
        )
        markdown = render_incident_markdown(incident)
        assert "Affected California residents" in markdown
        assert "Competent supervisory authority" in markdown

    def test_no_notification_obligations_renders_a_clean_statement_not_an_empty_section(
        self,
    ) -> None:
        incident = _incident()
        incident["notification_obligations"] = []
        markdown = render_incident_markdown(incident)
        assert "no notification" in markdown.lower() or "none identified" in markdown.lower()

    def test_escalation_is_rendered(self) -> None:
        markdown = render_incident_markdown(_incident())
        assert "escalat" in markdown.lower()

    def test_blocking_gap_is_rendered(self) -> None:
        markdown = render_incident_markdown(_incident())
        assert "Full list of affected recipients not yet confirmed." in markdown

    def test_advisory_disclosure_is_present(self) -> None:
        markdown = render_incident_markdown(_incident())
        assert "not a legal opinion" in markdown
        assert "accountable person" in markdown


def _review() -> dict:
    return {
        "title": "Annual review of MailerParish, Inc.",
        "vendor": {
            "name": "MailerParish, Inc.",
            "description": "A bulk-email vendor used to send the weekly bulletin.",
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
                "evidence": "Signed DPA on file, executed 2025-01-10.",
                "gap": None,
            },
            {
                "id": "security-controls-evidence",
                "status": "missing",
                "evidence": None,
                "gap": "No current SOC 2 report on file.",
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
            "rationale": "One baseline item unmet, with an open remediation commitment.",
        },
        "compliance": "Under GDPR Art. 28(3), the DPA must specify processing terms; "
        "current security-control evidence is required before the relationship continues.",
        "cst_reflection": "Closing this gap keeps the parishioners' trust intact.",
    }


class TestRenderReviewMarkdown:
    def test_renders_the_title_as_a_heading(self) -> None:
        markdown = render_review_markdown(_review())
        assert markdown.startswith("# Annual review of MailerParish, Inc.")

    def test_compliance_section_precedes_cst_reflection(self) -> None:
        markdown = render_review_markdown(_review())
        compliance_index = markdown.index("## Compliance")
        cst_index = markdown.index("## Catholic Social Teaching reflection")
        assert compliance_index < cst_index

    def test_overall_risk_is_rendered(self) -> None:
        markdown = render_review_markdown(_review())
        assert "moderate" in markdown.lower()

    def test_every_baseline_item_appears_with_its_status(self) -> None:
        markdown = render_review_markdown(_review())
        assert "dpa-in-place" in markdown
        assert "satisfied" in markdown.lower()
        assert "security-controls-evidence" in markdown
        assert "missing" in markdown.lower()

    def test_remediation_commitment_is_rendered_with_its_target_date(self) -> None:
        markdown = render_review_markdown(_review())
        assert "2026-09-15" in markdown
        assert "Vendor to provide an updated security questionnaire." in markdown

    def test_no_remediation_commitments_renders_a_clean_statement_not_an_empty_section(
        self,
    ) -> None:
        review = _review()
        review["remediation_commitments"] = []
        markdown = render_review_markdown(review)
        assert "no open remediation" in markdown.lower() or "none identified" in markdown.lower()

    def test_reassessment_due_is_rendered(self) -> None:
        markdown = render_review_markdown(_review())
        assert "2027-08-01" in markdown

    def test_advisory_disclosure_is_present(self) -> None:
        markdown = render_review_markdown(_review())
        assert "not a legal opinion" in markdown
        assert "accountable person" in markdown


def _retention_entry() -> dict:
    return {
        "title": "Parish bulletin subscriber list",
        "entry": {
            "description": "Email addresses and names collected via the sign-up form.",
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
            "rationale": "No re-confirmation has happened in over a year.",
            "target_date": "2026-09-01",
        },
        "compliance": "Under GDPR Art. 5(1)(e), retention must be actively justified.",
        "cst_reflection": "This keeps the review from lapsing into indefinite retention.",
    }


class TestRenderRetentionMarkdown:
    def test_renders_the_title_as_a_heading(self) -> None:
        markdown = render_retention_markdown(_retention_entry())
        assert markdown.startswith("# Parish bulletin subscriber list")

    def test_compliance_section_precedes_cst_reflection(self) -> None:
        markdown = render_retention_markdown(_retention_entry())
        compliance_index = markdown.index("## Compliance")
        cst_index = markdown.index("## Catholic Social Teaching reflection")
        assert compliance_index < cst_index

    def test_verdict_and_target_date_are_rendered(self) -> None:
        markdown = render_retention_markdown(_retention_entry())
        assert "needs-review" in markdown.lower()
        assert "2026-09-01" in markdown

    def test_current_verdict_with_no_target_date_renders_cleanly(self) -> None:
        entry = _retention_entry()
        entry["verdict"] = {
            "action": "current",
            "rationale": "Reviewed six months ago and retention remains justified.",
            "target_date": None,
        }
        markdown = render_retention_markdown(entry)
        assert "current" in markdown.lower()

    def test_advisory_disclosure_is_present(self) -> None:
        markdown = render_retention_markdown(_retention_entry())
        assert "not a legal opinion" in markdown
        assert "accountable person" in markdown


def _regulatory_change() -> dict:
    return {
        "title": "CPPA risk-assessment regulations take effect",
        "development": {
            "source": "California Privacy Protection Agency",
            "citation": "Cal. Code Regs. tit. 11, §§ 7150-7157",
            "summary": "New regulations requiring a risk assessment before high-risk processing.",
            "published_date": "2026-01-01",
        },
        "frameworks_considered": [
            {
                "id": "ccpa-cpra",
                "impacted": True,
                "basis": "This registry entry already cites the risk-assessment "
                "provision the new regulations flesh out.",
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
        "compliance": "Under Cal. Code Regs. tit. 11, § 7152, specified elements must "
        "be documented in the risk assessment.",
        "cst_reflection": "Keeping the registry current keeps the assessment honest.",
    }


class TestRenderRegulatoryChangeMarkdown:
    def test_renders_the_title_as_a_heading(self) -> None:
        markdown = render_regulatory_change_markdown(_regulatory_change())
        assert markdown.startswith("# CPPA risk-assessment regulations take effect")

    def test_compliance_section_precedes_cst_reflection(self) -> None:
        markdown = render_regulatory_change_markdown(_regulatory_change())
        compliance_index = markdown.index("## Compliance")
        cst_index = markdown.index("## Catholic Social Teaching reflection")
        assert compliance_index < cst_index

    def test_development_source_and_citation_are_rendered(self) -> None:
        markdown = render_regulatory_change_markdown(_regulatory_change())
        assert "California Privacy Protection Agency" in markdown
        assert "Cal. Code Regs. tit. 11, §§ 7150-7157" in markdown

    def test_recommended_action_is_rendered(self) -> None:
        markdown = render_regulatory_change_markdown(_regulatory_change())
        assert "update-required-element" in markdown.lower()
        assert "ccpa-cpra" in markdown

    def test_advisory_disclosure_is_present(self) -> None:
        markdown = render_regulatory_change_markdown(_regulatory_change())
        assert "not a legal opinion" in markdown
        assert "accountable person" in markdown


class TestSlugify:
    def test_title_becomes_hyphenated_slug(self) -> None:
        assert slugify("Parish Bulletin Sign-Up Form") == "Parish-Bulletin-Sign-Up-Form"

    def test_strips_characters_outside_letters_numbers_and_hyphens(self) -> None:
        assert slugify("A/B Test: Signup?") == "A-B-Test-Signup"


class TestWriteReport:
    def test_writes_a_dated_slugified_file_and_returns_its_path(self, tmp_path: Path) -> None:
        out_dir = tmp_path / "reports"
        written = write_report(_assessment(), out_dir, today=datetime.date(2026, 8, 11))
        assert written.parent == out_dir
        assert written.name == "2026-08-11-Parish-Bulletin-Sign-Up-Form.md"
        assert written.read_text().startswith("# Parish Bulletin Sign-Up Form")

    def test_creates_out_dir_if_missing(self, tmp_path: Path) -> None:
        out_dir = tmp_path / "does" / "not" / "exist" / "yet"
        written = write_report(_assessment(), out_dir, today=datetime.date(2026, 8, 11))
        assert written.exists()

    def test_render_fn_selects_which_renderer_writes_the_report(self, tmp_path: Path) -> None:
        out_dir = tmp_path / "reports"
        written = write_report(
            _triage(),
            out_dir,
            render_fn=render_triage_markdown,
            today=datetime.date(2026, 8, 11),
        )
        assert written.name == "2026-08-11-Access-request-from-a-returning-parishioner.md"
        assert "Art. 12(3)" in written.read_text()
