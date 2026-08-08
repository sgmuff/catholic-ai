"""The shape of a CST assessment, and how it's rendered and written. A
report is a finding document, not a verdict — see rubric/criteria.md. It
either states a bright-line incompatibility plainly, or gives all eight
principles a graded score, a mitigation for anything scoring low, and an
"ideal" describing fuller conformity beyond that floor. It never says
"pass" or "fail," and it always names itself advisory and unreviewed
(beta — see CONTRIBUTING.md).

The same two-stage rubric runs against either of two subjects: a described,
planned AI use (`Subject.kind == "use_case"`), or an actual prompt/response
pair from a deployed LLM being audited after the fact
(`Subject.kind == "llm_interaction"`). The rubric doesn't change between the
two — only what's being judged does.
"""

from __future__ import annotations

import re
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
    """Stage 2 of rubric/criteria.md: one of the eight principles' scores.

    `mitigation` is the floor: the minimum change that makes a low score
    acceptable. `ideal` is not a fallback for when `mitigation` is absent —
    every rating carries one, describing fuller conformity to the principle
    than the floor requires, whether or not there's a floor to clear.
    """

    principle_id: str
    principle_name: str
    score: int
    rationale: str
    mitigation: str | None
    ideal: str
    contested: bool = False


@dataclass(frozen=True)
class OverallRecommendation:
    """A holistic judgment made after all eight principles are scored, not
    an average of them: given the full set of scores and mitigations
    together, is the use still viable, and what follows from that."""

    viable: bool
    narrative: str


@dataclass(frozen=True)
class Assessment:
    subject: Subject
    follow_up_questions: tuple[str, ...]
    bright_line: BrightLineFinding
    ratings: tuple[PrincipleRating, ...]
    overall: OverallRecommendation | None
    non_negotiable_title: str | None
    non_negotiable_citations: tuple[str, ...]
    generated_at: datetime
    title: str | None


_DISCLAIMER = (
    "This is an advisory finding, not a certification or a pass/fail verdict. "
    "The reasoning behind it is a working interpretation of Catholic Social "
    "Teaching, still unreviewed, not a canonical magisterial one. A person "
    "makes the final call, not this report: specifically, a parish's pastor "
    "or someone else there well versed in Catholic theology should review "
    "this finding before it's acted on."
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


def _title_case_slug(text: str, max_len: int = 60) -> str:
    """Turns a label into the Title-Case-With-Hyphens form used in report
    filenames (YYYY-MM-DD-Brief-Description.md) — capitalizes each word's
    first letter without lowercasing the rest, so an acronym like "AI"
    survives intact, and truncates on whole words rather than mid-word."""
    words = [w[0].upper() + w[1:] if w else w for w in re.split(r"[^A-Za-z0-9]+", text) if w]
    kept: list[str] = []
    length = 0
    for word in words:
        added = len(word) + (1 if kept else 0)
        if length + added > max_len:
            break
        kept.append(word)
        length += added
    return "-".join(kept) or "Untitled"


def _subject_one_liner(assessment: Assessment) -> str:
    """A short label for this assessment's subject — used in the index and
    as a fallback report title. Prefers the given `title`; otherwise
    derives something short from the subject itself rather than leaving an
    index row blank."""
    if assessment.title:
        return assessment.title
    subject = assessment.subject
    if subject.kind == "llm_interaction":
        return f"Interaction audit — {subject.model}"
    text = (subject.use_description or "").strip().replace("\n", " ")
    return text if len(text) <= 80 else text[:77] + "..."


def _verdict_one_liner(assessment: Assessment) -> str:
    if assessment.bright_line.matched:
        return f"Incompatible — {assessment.non_negotiable_title}"
    if assessment.overall is not None:
        return (
            "Viable (with mitigations)" if assessment.overall.viable else "Not viable as described"
        )
    return "Graded"


def render_markdown(assessment: Assessment) -> str:
    heading = "# CST alignment assessment"
    if assessment.title:
        heading = f"{heading}: {assessment.title}"
    lines = [
        heading,
        "",
        _DISCLAIMER,
        "",
        f"- Generated: {assessment.generated_at.isoformat()}",
        "",
        *_render_subject(assessment.subject),
    ]

    if not assessment.bright_line.matched and assessment.overall is not None:
        lines.append("## At a glance")
        lines.append("")
        glance = (
            "Viable, with the mitigations below"
            if assessment.overall.viable
            else "Not viable as described"
        )
        lines.append(f"**{glance}.** {_summary_line(assessment.ratings)}")
        lines.append("")

    if assessment.follow_up_questions:
        lines.append("## Follow-up questions asked")
        lines.append("")
        lines.extend(_bulleted(list(assessment.follow_up_questions)))

    if assessment.bright_line.matched:
        lines.append("## Verdict: incompatible with Catholic Social Teaching")
        lines.append("")
        lines.append(
            f"This {_subject_noun(assessment.subject)} matches a line Catholic Social "
            f"Teaching treats as settled, not open to weighing: **{assessment.non_negotiable_title}**."
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
            "several to be weighed — the tradition treats it as a line that ends the "
            "assessment the moment it's crossed."
        )
        lines.append("")
        return "\n".join(lines)

    lines.append("## Principle-by-principle rating")
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
        lines.append(f"**Ideally:** {r.ideal}")
        lines.append("")

    if assessment.overall is not None:
        lines.append("## Overall assessment")
        lines.append("")
        verdict = (
            "Viable, with the mitigations above"
            if assessment.overall.viable
            else "Not viable as described"
        )
        lines.append(f"**{verdict}.**")
        lines.append("")
        lines.append(assessment.overall.narrative)
        lines.append("")

    return "\n".join(lines)


_INDEX_HEADER = (
    "# CST assessment index\n\n"
    "Every report generated in this directory, oldest first.\n\n"
    "| Date | Subject | Verdict | Report |\n"
    "| --- | --- | --- | --- |\n"
)


def _update_index(out_dir: Path, assessment: Assessment, report_path: Path) -> None:
    index_path = out_dir / "INDEX.md"
    if not index_path.exists():
        index_path.write_text(_INDEX_HEADER)
    date = assessment.generated_at.strftime("%Y-%m-%d")
    subject = _subject_one_liner(assessment)
    verdict = _verdict_one_liner(assessment)
    row = f"| {date} | {subject} | {verdict} | [{report_path.name}]({report_path.name}) |\n"
    with index_path.open("a") as f:
        f.write(row)


def write_report(assessment: Assessment, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    date = assessment.generated_at.strftime("%Y-%m-%d")
    slug = _title_case_slug(_subject_one_liner(assessment))
    base = f"{date}-{slug}"
    path = out_dir / f"{base}.md"
    suffix = 2
    while path.exists():
        path = out_dir / f"{base}-{suffix}.md"
        suffix += 1
    path.write_text(render_markdown(assessment))
    _update_index(out_dir, assessment, path)
    return path


def now_utc() -> datetime:
    return datetime.now(UTC)
