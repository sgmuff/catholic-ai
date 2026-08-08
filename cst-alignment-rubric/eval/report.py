"""The shape of a CST assessment, and how it's rendered and written. A
report is a finding document, not a verdict — see rubric/criteria.md. It
either states a bright-line incompatibility plainly, or gives all eight
principles a graded score with a mitigation for anything scoring low. It
never says "pass" or "fail," and it always names itself advisory and
unreviewed (beta — see CONTRIBUTING.md).

The same two-stage rubric runs against either of two subjects: a described,
planned AI use (`Subject.kind == "use_case"`), or an actual prompt/response
pair from a deployed LLM being audited after the fact
(`Subject.kind == "llm_interaction"`). The rubric doesn't change between the
two — only what's being judged does.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

SubjectKind = Literal["use_case", "llm_interaction"]


@dataclass(frozen=True)
class Subject:
    """What's being assessed. Exactly one shape is populated, matching
    `kind` — see eval/assessment.py's `_validate_subject` for how a raw
    assessment resolves to one or the other.
    """

    kind: SubjectKind
    use_description: str | None = None
    prompt: str | None = None
    response: str | None = None
    model: str | None = None


@dataclass(frozen=True)
class BrightLineFinding:
    """Stage 1 of rubric/criteria.md: does the subject match one of
    principles/non-negotiables.yaml's items? If so, the assessment stops
    here — see Assessment.ratings, which is empty when matched=True.
    """

    matched: bool
    non_negotiable_id: str | None = None
    explanation: str | None = None


@dataclass(frozen=True)
class PrincipleRating:
    """Stage 2 of rubric/criteria.md: one of the eight principles' scores."""

    principle_id: str
    principle_name: str
    score: int
    rationale: str
    mitigation: str | None
    contested: bool = False


@dataclass(frozen=True)
class Assessment:
    subject: Subject
    follow_up_questions: tuple[str, ...]
    bright_line: BrightLineFinding
    ratings: tuple[PrincipleRating, ...]
    non_negotiable_title: str | None
    non_negotiable_citations: tuple[str, ...]
    generated_at: datetime


_DISCLAIMER = (
    "This is an advisory finding, not a certification or a pass/fail verdict. "
    "The principle content behind it is unreviewed and in beta (see CONTRIBUTING.md); "
    "it reflects a working interpretation of Catholic Social Teaching, not a "
    "canonical magisterial one. A person makes the final call, not this report."
)


def _subject_noun(subject: Subject) -> str:
    """The word the bright-line verdict uses to refer to what it matched —
    a described use is judged as a plan, an interaction is judged by what
    the response actually said."""
    return "response" if subject.kind == "llm_interaction" else "use"


def _blockquote(text: str) -> list[str]:
    lines = [f"> {line}" if line else ">" for line in text.splitlines()]
    return lines or [">"]


def _bulleted(items: list[str]) -> list[str]:
    """Renders a bullet list with a blank line between items — a run of
    bullets with no spacing between them is hard to scan once any item
    wraps past one line."""
    lines: list[str] = []
    for item in items:
        lines.append(f"- {item}")
        lines.append("")
    return lines


def _summary_line(ratings: tuple[PrincipleRating, ...]) -> str:
    """One computed sentence up front so a reader isn't required to read
    all eight rows before knowing the overall shape of the result. Purely
    derived from the ratings already present — no new judgment is made
    here, only arithmetic over scores that were already assigned."""
    total = len(ratings)
    high = sum(1 for r in ratings if r.score >= 4)
    low = [r for r in ratings if r.mitigation]
    contested = [r for r in ratings if r.contested]

    parts = [f"{high} of {total} principles scored 4 or higher"]
    if low:
        named = ", ".join(f"{r.principle_name} ({r.score})" for r in low)
        parts.append(f"{len(low)} scored 3 or below: {named}")
    if contested:
        named = ", ".join(r.principle_name for r in contested)
        parts.append(f"{len(contested)} flagged contested: {named}")
    return "; ".join(parts) + "."


def _render_subject(subject: Subject) -> list[str]:
    if subject.kind == "llm_interaction":
        lines = ["## Audited interaction", "", f"**Model:** {subject.model}", "", "**Prompt:**", ""]
        lines.extend(_blockquote(subject.prompt or ""))
        lines.append("")
        lines.append("**Response:**")
        lines.append("")
        lines.extend(_blockquote(subject.response or ""))
        lines.append("")
        return lines
    return ["## Described use", "", subject.use_description or "", ""]


def render_markdown(assessment: Assessment) -> str:
    lines = [
        "# CST alignment assessment",
        "",
        _DISCLAIMER,
        "",
        f"- Generated: {assessment.generated_at.isoformat()}",
        "",
        *_render_subject(assessment.subject),
    ]

    if assessment.follow_up_questions:
        lines.append("## Follow-up questions asked")
        lines.append("")
        lines.extend(_bulleted(list(assessment.follow_up_questions)))

    if assessment.bright_line.matched:
        lines.append("## Verdict: incompatible with Catholic Social Teaching")
        lines.append("")
        lines.append(
            f"This {_subject_noun(assessment.subject)} matches a non-negotiable in "
            f"`principles/non-negotiables.yaml`: **{assessment.non_negotiable_title}** "
            f"(`{assessment.bright_line.non_negotiable_id}`)."
        )
        lines.append("")
        lines.append(assessment.bright_line.explanation or "")
        lines.append("")
        if assessment.non_negotiable_citations:
            lines.append("Citations:")
            lines.append("")
            lines.extend(_bulleted(list(assessment.non_negotiable_citations)))
        lines.append(
            "No principle-by-principle score follows. This is not one factor among "
            "several to be weighed; see rubric/criteria.md, Stage 1."
        )
        lines.append("")
        return "\n".join(lines)

    lines.append("## Principle-by-principle rating")
    lines.append("")
    lines.append(_summary_line(assessment.ratings))
    lines.append("")
    for r in assessment.ratings:
        contested_tag = " *(contested: route to human review)*" if r.contested else ""
        lines.append(f"### {r.principle_name}: {r.score}/5{contested_tag}")
        lines.append("")
        lines.append(r.rationale)
        lines.append("")
        if r.mitigation:
            lines.append(f"**Mitigation:** {r.mitigation}")
            lines.append("")

    low_scores = [r for r in assessment.ratings if r.mitigation]
    if low_scores:
        lines.append("## Mitigations")
        lines.append("")
        lines.append("Scored 3 or below; see the mitigation under each principle above:")
        lines.append("")
        lines.extend(_bulleted([f"{r.principle_name} ({r.score}/5)" for r in low_scores]))

    contested = [r for r in assessment.ratings if r.contested]
    if contested:
        lines.append("## Contested")
        lines.append("")
        lines.append(
            "The following principles reflect a genuine tension in the tradition "
            "itself, not just a low score; route these to a person before acting "
            "on the number alone. See each principle's rationale above:"
        )
        lines.append("")
        lines.extend(_bulleted([f"{r.principle_name} ({r.score}/5)" for r in contested]))

    return "\n".join(lines)


def write_report(assessment: Assessment, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = assessment.generated_at.strftime("%Y%m%dT%H%M%SZ") + ".md"
    path = out_dir / filename
    path.write_text(render_markdown(assessment))
    return path


def now_utc() -> datetime:
    return datetime.now(UTC)
