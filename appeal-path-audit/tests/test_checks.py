import pytest

from appeal_path_audit.checks import CHECKS, keyword_absence, keyword_presence


def test_keyword_presence_passes_when_required_substring_present():
    result = keyword_presence(
        {"required_substrings": ["automated decision"]},
        "This determination was made using an automated decision system.",
    )

    assert result.verdict == "pass"


def test_keyword_presence_fails_when_none_present():
    result = keyword_presence({"required_substrings": ["automated decision"]}, "You were denied.")

    assert result.verdict == "fail"


def test_keyword_presence_is_case_insensitive():
    result = keyword_presence(
        {"required_substrings": ["RIGHT TO APPEAL"]}, "you have a right to appeal this decision."
    )

    assert result.verdict == "pass"


def test_keyword_presence_raises_on_missing_args():
    with pytest.raises(ValueError, match="required_substrings"):
        keyword_presence({}, "anything")


def test_keyword_absence_passes_when_nothing_forbidden_present():
    result = keyword_absence(
        {"forbidden_substrings": ["final and unappealable"]}, "You may appeal."
    )

    assert result.verdict == "pass"


def test_keyword_absence_fails_when_forbidden_substring_present():
    result = keyword_absence(
        {"forbidden_substrings": ["final and unappealable"]},
        "This decision is final and unappealable.",
    )

    assert result.verdict == "fail"
    assert "final and unappealable" in result.explanation


def test_keyword_absence_raises_on_missing_args():
    with pytest.raises(ValueError, match="forbidden_substrings"):
        keyword_absence({}, "anything")


def test_checks_registry_contains_both():
    assert set(CHECKS) == {"keyword_presence", "keyword_absence"}
