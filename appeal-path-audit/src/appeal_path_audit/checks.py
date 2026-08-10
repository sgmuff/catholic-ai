"""Scores a single (notice text, rule) pair. Two checks, both mechanical:
does required language appear, or does forbidden language appear. Anything
that can't be reduced to a text pattern — does this notice's phrasing
actually give an ordinary reader a genuine understanding of their right to
appeal — isn't something this module tries to judge; a rule that needs that
kind of reading stays out of the corpus rather than being approximated by a
keyword list that would just be wrong sometimes.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

Verdict = Literal["pass", "fail"]


@dataclass(frozen=True)
class CheckResult:
    verdict: Verdict
    explanation: str


CheckFn = Callable[[dict[str, object], str], CheckResult]


def keyword_presence(check_args: dict[str, object], text: str) -> CheckResult:
    """Fails if none of `required_substrings` appears in the text
    (case-insensitive) — used to require a disclosure element be present."""
    required = _string_list(check_args, "required_substrings")
    lowered = text.lower()
    hits = [s for s in required if s.lower() in lowered]
    if not hits:
        return CheckResult(
            verdict="fail", explanation=f"none of the required substring(s) present: {required}"
        )
    return CheckResult(verdict="pass", explanation=f"required substring present: {hits}")


def keyword_absence(check_args: dict[str, object], text: str) -> CheckResult:
    """Fails if any of `forbidden_substrings` appears in the text
    (case-insensitive) — used to flag misleading language a notice
    shouldn't contain."""
    forbidden = _string_list(check_args, "forbidden_substrings")
    lowered = text.lower()
    hits = [s for s in forbidden if s.lower() in lowered]
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
