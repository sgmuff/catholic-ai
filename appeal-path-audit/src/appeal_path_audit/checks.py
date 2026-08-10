"""Scores a single (notice text, rule) pair. Two checks, both mechanical:
does required language appear, or does forbidden language appear. Anything
that can't be reduced to a text pattern — does this notice's phrasing
actually give an ordinary reader a genuine understanding of their right to
appeal — isn't something this module tries to judge; a rule that needs that
kind of reading stays out of the corpus rather than being approximated by a
keyword list that would just be wrong sometimes.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

Verdict = Literal["pass", "fail"]


@dataclass(frozen=True)
class CheckResult:
    verdict: Verdict
    explanation: str


CheckFn = Callable[[dict[str, object], str], CheckResult]

#: A substring match this close after "not automated" or "no human review" etc.
#: doesn't count as a genuine hit — the sentence is disclaiming the term, not
#: using it. A fixed character window is a blunt instrument, but the check
#: this guards is itself a blunt substring match; this only needs to catch
#: the common case, not parse the sentence.
_NEGATION_CUES = re.compile(r"\b(?:not|no|never|without)\b|n't")
_NEGATION_WINDOW_CHARS = 40


def _has_unnegated_occurrence(lowered_text: str, substring_lower: str) -> bool:
    start = 0
    while True:
        idx = lowered_text.find(substring_lower, start)
        if idx == -1:
            return False
        window = lowered_text[max(0, idx - _NEGATION_WINDOW_CHARS) : idx]
        # Don't let a negation in an earlier sentence taint this one.
        sentence_start = max(window.rfind("."), window.rfind("!"), window.rfind("?"))
        if sentence_start != -1:
            window = window[sentence_start + 1 :]
        if not _NEGATION_CUES.search(window):
            return True
        start = idx + 1


def keyword_presence(check_args: dict[str, object], text: str) -> CheckResult:
    """Fails if none of `required_substrings` appears in the text
    (case-insensitive) in a non-negated context — used to require a
    disclosure element be genuinely present, not merely mentioned to be
    disclaimed (e.g. "this was not an automated decision" doesn't disclose
    automation just because it contains the word)."""
    required = _string_list(check_args, "required_substrings")
    lowered = text.lower()
    hits = [s for s in required if _has_unnegated_occurrence(lowered, s.lower())]
    if not hits:
        negated_only = [s for s in required if s.lower() in lowered and s not in hits]
        if negated_only:
            return CheckResult(
                verdict="fail",
                explanation=(f"substring(s) present only in a negated context: {negated_only}"),
            )
        return CheckResult(
            verdict="fail", explanation=f"none of the required substring(s) present: {required}"
        )
    return CheckResult(verdict="pass", explanation=f"required substring present: {hits}")


def keyword_absence(check_args: dict[str, object], text: str) -> CheckResult:
    """Fails if any of `forbidden_substrings` appears in the text
    (case-insensitive) in a non-negated context — used to flag misleading
    language a notice shouldn't contain. A forbidden phrase that's itself
    being negated (e.g. "this decision is not final") isn't the violation
    the rule is looking for."""
    forbidden = _string_list(check_args, "forbidden_substrings")
    lowered = text.lower()
    hits = [s for s in forbidden if _has_unnegated_occurrence(lowered, s.lower())]
    if hits:
        return CheckResult(verdict="fail", explanation=f"forbidden substring(s) present: {hits}")
    return CheckResult(verdict="pass", explanation="no forbidden substring present")


def _string_list(check_args: dict[str, object], field: str) -> list[str]:
    raw = check_args.get(field)
    if not isinstance(raw, list) or not raw or not all(isinstance(s, str) for s in raw):
        raise ValueError(f"check_args.{field!r} must be a non-empty list of strings")
    return list(raw)


CHECKS: dict[str, CheckFn] = {
    "keyword_presence": keyword_presence,
    "keyword_absence": keyword_absence,
}
