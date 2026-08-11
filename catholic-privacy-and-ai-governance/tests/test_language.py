import pytest

from privacy_and_ai_governance.language import (
    CST_TERMS,
    ComplianceLanguageError,
    check_compliance_language,
    find_cst_language,
)


class TestFindCstLanguage:
    def test_clean_regulatory_text_returns_nothing(self) -> None:
        text = (
            "Under GDPR Art. 35(1), this processing is likely to result in a "
            "high risk to the rights and freedoms of natural persons and "
            "therefore requires a DPIA before processing begins."
        )
        assert find_cst_language(text) == []

    @pytest.mark.parametrize("term", CST_TERMS)
    def test_each_blocked_term_is_detected(self, term: str) -> None:
        text = f"This use is grounded in {term} and therefore acceptable."
        assert term in find_cst_language(text)

    def test_matching_is_case_insensitive(self) -> None:
        assert "solidarity" in find_cst_language("This reflects deep SOLIDARITY.")

    def test_reports_every_offending_term_found(self) -> None:
        text = "This appeals to both personalism and subsidiarity at once."
        found = find_cst_language(text)
        assert "personalism" in found
        assert "subsidiarity" in found


class TestCheckComplianceLanguage:
    def test_clean_text_does_not_raise(self) -> None:
        check_compliance_language("The controller must identify a lawful basis under Art. 6.")

    def test_poisoned_text_raises_with_offending_terms_named(self) -> None:
        with pytest.raises(ComplianceLanguageError, match="solidarity"):
            check_compliance_language(
                "In solidarity with the vulnerable, retention must be limited."
            )
