"""Enforces build-plan.md §2.1: Catholic language is additive, never
substitutive. A report's ``compliance`` section stays in the applicable
framework's own regulatory register; Catholic Social Teaching vocabulary
belongs only in ``cst_reflection``, never here.
"""

from __future__ import annotations

CST_TERMS: list[str] = [
    "personalism",
    "solidarity",
    "subsidiarity",
    "common good",
    "Magnifica Humanitas",
    "imago dei",
    "dignity of the human person",
]


class ComplianceLanguageError(Exception):
    """Raised when CST vocabulary leaks into a compliance section (§2.1)."""


def find_cst_language(text: str) -> list[str]:
    """Case-insensitive scan of *text* for the §2.1 blocklist. Returns the
    offending terms found, in blocklist order; an empty list means the text
    is clean.
    """
    lowered = text.lower()
    return [term for term in CST_TERMS if term.lower() in lowered]


def check_compliance_language(compliance_text: str) -> None:
    """Raises ComplianceLanguageError if *compliance_text* contains any §2.1
    blocklist term.
    """
    found = find_cst_language(compliance_text)
    if found:
        raise ComplianceLanguageError(
            "Catholic Social Teaching vocabulary found in the compliance section "
            f"(§2.1 violation): {', '.join(found)}. Compliance findings must stay "
            "in the applicable framework's own regulatory register; move this "
            "reasoning to cst_reflection instead."
        )
