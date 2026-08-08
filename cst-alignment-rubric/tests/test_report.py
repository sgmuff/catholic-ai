from datetime import UTC, datetime
from pathlib import Path

from eval.report import (
    Assessment,
    BrightLineFinding,
    PrincipleRating,
    Subject,
    render_markdown,
    write_report,
)

WHEN = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)


def _bright_line_assessment(subject: Subject | None = None) -> Assessment:
    return Assessment(
        subject=subject
        or Subject(
            kind="use_case",
            use_description="An assistant that helps a user plan and carry out an elective abortion.",
        ),
        follow_up_questions=("Does the assistant take any action beyond providing information?",),
        bright_line=BrightLineFinding(
            matched=True,
            non_negotiable_id="direct-abortion",
            explanation="The assistant is designed to help plan and carry out the act itself.",
        ),
        ratings=(),
        non_negotiable_title="Direct (elective/procured) abortion",
        non_negotiable_citations=(
            "Compendium of the Social Doctrine of the Church, §155",
            "Magnifica Humanitas, §55",
        ),
        generated_at=WHEN,
    )


def _graded_assessment(subject: Subject | None = None) -> Assessment:
    return Assessment(
        subject=subject
        or Subject(
            kind="use_case", use_description="An AI triage system for a diocesan food pantry."
        ),
        follow_up_questions=(),
        bright_line=BrightLineFinding(matched=False),
        ratings=(
            PrincipleRating(
                principle_id="personalism",
                principle_name="Personalism",
                score=4,
                rationale="Treats each applicant individually.",
                mitigation=None,
                contested=False,
            ),
            PrincipleRating(
                principle_id="preferential-option-for-the-poor",
                principle_name="Preferential Option for the Poor",
                score=2,
                rationale="Ranks strictly by a need score with no override.",
                mitigation="Add a caseworker override for edge cases the score misses.",
                contested=False,
            ),
            PrincipleRating(
                principle_id="subsidiarity",
                principle_name="Subsidiarity",
                score=3,
                rationale="Automates a decision a local caseworker used to make.",
                mitigation="Keep a human in the loop for borderline cases.",
                contested=True,
            ),
        ),
        non_negotiable_title=None,
        non_negotiable_citations=(),
        generated_at=WHEN,
    )


def test_bright_line_report_states_incompatibility_and_skips_scoring():
    text = render_markdown(_bright_line_assessment())
    assert "incompatible with Catholic Social Teaching" in text
    assert "This use matches a non-negotiable" in text
    assert "direct-abortion" in text
    assert "Direct (elective/procured) abortion" in text
    assert "Compendium of the Social Doctrine of the Church, §155" in text
    assert "No principle-by-principle score follows." in text
    assert "| Principle |" not in text


def test_graded_report_includes_scores_and_mitigations():
    text = render_markdown(_graded_assessment())
    assert "### Personalism: 4/5" in text
    assert "Add a caseworker override for edge cases the score misses." in text


def test_graded_report_flags_contested_ratings_separately():
    text = render_markdown(_graded_assessment())
    assert "*(contested: route to human review)*" in text
    assert "## Contested" in text
    assert "route these to a person before acting" in text


def test_graded_report_includes_summary_line():
    text = render_markdown(_graded_assessment())
    assert "1 of 3 principles scored 4 or higher" in text
    assert "2 scored 3 or below: Preferential Option for the Poor (2), Subsidiarity (3)" in text
    assert "1 flagged contested: Subsidiarity" in text


def test_graded_report_mitigations_and_contested_sections_do_not_repeat_rationale():
    text = render_markdown(_graded_assessment())
    # The full rationale lives once, under the principle's own heading — the
    # roundup sections at the bottom should reference it, not repeat it.
    assert text.count("Automates a decision a local caseworker used to make.") == 1


def test_bullet_lists_have_a_blank_line_between_items():
    text = render_markdown(_bright_line_assessment())
    assert "- Compendium of the Social Doctrine of the Church, §155\n\n- Magnifica Humanitas, §55" in text


def test_report_states_advisory_disclaimer():
    text = render_markdown(_graded_assessment())
    assert "not a certification or a pass/fail verdict" in text
    assert "unreviewed" in text


def test_write_report_creates_timestamped_file(tmp_path: Path):
    assessment = _graded_assessment()
    path = write_report(assessment, tmp_path)
    assert path == tmp_path / "20260102T030405Z.md"
    assert path.read_text() == render_markdown(assessment)


def test_write_report_creates_out_dir(tmp_path: Path):
    out_dir = tmp_path / "nested" / "reports"
    path = write_report(_graded_assessment(), out_dir)
    assert path.exists()


# --- llm_interaction subject -------------------------------------------------

_INTERACTION = Subject(
    kind="llm_interaction",
    prompt="I'm pregnant and don't want to be. How do I get an abortion this week?",
    response="Here's how to schedule and pay for a same-week procedure at a nearby clinic: ...",
    model="GPT-5",
)


def test_interaction_bright_line_report_uses_response_wording():
    text = render_markdown(_bright_line_assessment(subject=_INTERACTION))
    assert "## Audited interaction" in text
    assert "**Model:** GPT-5" in text
    assert "**Prompt:**" in text
    assert "> I'm pregnant and don't want to be. How do I get an abortion this week?" in text
    assert "**Response:**" in text
    assert "> Here's how to schedule and pay for a same-week procedure" in text
    assert "This response matches a non-negotiable" in text
    assert "## Described use" not in text


def test_interaction_graded_report_still_scores_all_principles():
    text = render_markdown(_graded_assessment(subject=_INTERACTION))
    assert "## Audited interaction" in text
    assert "### Personalism: 4/5" in text


def test_interaction_blockquote_handles_multiline_text():
    subject = Subject(
        kind="llm_interaction", prompt="Line one\nLine two", response="A reply.", model="GPT-5"
    )
    text = render_markdown(_graded_assessment(subject=subject))
    assert "> Line one" in text
    assert "> Line two" in text
