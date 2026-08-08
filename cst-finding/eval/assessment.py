"""Validates a raw assessment (as produced by the `cst-finding` skill,
either interviewing a user about a planned AI use or auditing an actual
prompt/response pair) against the real principle and non-negotiable
definitions in `principles/`, then renders and writes the advisory report —
see rubric/criteria.md for the two-stage rubric this implements.

Deliberately does not call any LLM. The judgment — does the subject match a
non-negotiable? what does each principle score, and why? — is made by
whoever (or whatever) is conducting the assessment, reasoning directly
against principles/*.yaml. This module's job is narrower: catch a
fabricated principle id, a missing rationale, a low score with no
mitigation, or any other shape that doesn't check out, and fail loudly
rather than render a report that looks more authoritative than the
judgment behind it actually is.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from eval.principles import (
    NonNegotiable,
    Principle,
    load_non_negotiables,
    load_principles,
)
from eval.report import (
    Assessment,
    BrightLineFinding,
    PrincipleRating,
    Subject,
    now_utc,
    write_report,
)

MIN_SCORE = 1
MAX_SCORE = 5

#: Scores at or below this require a mitigation — see rubric/criteria.md,
#: "Stage 2 — the graded rubric."
MITIGATION_THRESHOLD = 3


def _validate_bright_line(
    raw: dict[str, Any], non_negotiables: dict[str, NonNegotiable]
) -> BrightLineFinding:
    matched = bool(raw.get("matched", False))
    if not matched:
        return BrightLineFinding(matched=False)

    nn_id = raw.get("non_negotiable_id")
    if nn_id not in non_negotiables:
        raise ValueError(
            f"bright-line match references unknown non-negotiable id {nn_id!r}; "
            f"must be one of {sorted(non_negotiables)}"
        )
    explanation = raw.get("explanation")
    if not explanation:
        raise ValueError("a bright-line match requires a non-empty 'explanation'")
    return BrightLineFinding(
        matched=True, non_negotiable_id=str(nn_id), explanation=str(explanation).strip()
    )


def _validate_rating(raw: dict[str, Any], principles: dict[str, Principle]) -> PrincipleRating:
    principle_id = raw.get("principle_id")
    if principle_id not in principles:
        raise ValueError(
            f"rating references unknown principle id {principle_id!r}; "
            f"must be one of {sorted(principles)}"
        )
    score = raw.get("score")
    if not isinstance(score, int) or isinstance(score, bool) or not MIN_SCORE <= score <= MAX_SCORE:
        raise ValueError(
            f"{principle_id}: score {score!r} must be an integer {MIN_SCORE}-{MAX_SCORE}"
        )
    rationale = raw.get("rationale")
    if not rationale:
        raise ValueError(f"{principle_id}: 'rationale' is required")
    mitigation = raw.get("mitigation")
    if score <= MITIGATION_THRESHOLD and not mitigation:
        raise ValueError(
            f"{principle_id}: scored {score} (<= {MITIGATION_THRESHOLD}) but has no 'mitigation' "
            "— see rubric/criteria.md, Stage 2"
        )
    return PrincipleRating(
        principle_id=str(principle_id),
        principle_name=principles[str(principle_id)].name,
        score=score,
        rationale=str(rationale).strip(),
        mitigation=str(mitigation).strip() if mitigation else None,
        contested=bool(raw.get("contested", False)),
    )


def _validate_subject(raw: dict[str, Any]) -> Subject:
    """Exactly one of two shapes: `use_description` (a planned/described AI
    use), or `prompt` + `response` + `model` together (an actual interaction
    to audit — `model` names which LLM produced the response, since that's
    part of the record of what was audited). Neither, or a mix of both
    shapes, is rejected rather than guessed at.
    """
    use_description = raw.get("use_description")
    prompt = raw.get("prompt")
    response = raw.get("response")
    model = raw.get("model")

    has_use_case = bool(use_description)
    has_interaction = bool(prompt) or bool(response) or bool(model)

    if has_use_case and has_interaction:
        raise ValueError(
            "provide either 'use_description' (a planned/described AI use) or "
            "'prompt' + 'response' + 'model' (an actual interaction to audit), not both"
        )
    if has_interaction:
        if not prompt or not response or not model:
            raise ValueError(
                "auditing an interaction requires 'prompt', 'response', and 'model' "
                "(which LLM produced the response) together, not just some of them"
            )
        return Subject(
            kind="llm_interaction",
            prompt=str(prompt).strip(),
            response=str(response).strip(),
            model=str(model).strip(),
        )
    if has_use_case:
        return Subject(kind="use_case", use_description=str(use_description).strip())
    raise ValueError("provide either 'use_description', or 'prompt' + 'response' + 'model'")


def build_assessment(raw: dict[str, Any], principles_dir: Path) -> Assessment:
    """Validates `raw` against `principles_dir`'s real content and returns a
    ready-to-render Assessment. Raises ValueError, naming what's wrong, on
    anything that doesn't check out.
    """
    principles = load_principles(principles_dir)
    non_negotiables = {nn.id: nn for nn in load_non_negotiables(principles_dir)}

    subject = _validate_subject(raw)

    follow_ups = tuple(str(q).strip() for q in raw.get("follow_up_questions", []))

    bright_line = _validate_bright_line(raw.get("bright_line") or {}, non_negotiables)

    ratings: tuple[PrincipleRating, ...] = ()
    non_negotiable_title: str | None = None
    non_negotiable_citations: tuple[str, ...] = ()

    if bright_line.matched:
        matched_item = non_negotiables[bright_line.non_negotiable_id]  # type: ignore[index]
        non_negotiable_title = matched_item.title
        non_negotiable_citations = tuple(
            f"{c.source}, {c.reference}" for c in matched_item.citations
        )
    else:
        raw_ratings = raw.get("ratings")
        if not raw_ratings:
            raise ValueError(
                "no bright-line match, but 'ratings' is empty — all 8 principles need a score"
            )
        ratings = tuple(_validate_rating(r, principles) for r in raw_ratings)
        rated_ids = {r.principle_id for r in ratings}
        missing_ids = set(principles) - rated_ids
        if missing_ids:
            raise ValueError(f"missing ratings for principle(s): {sorted(missing_ids)}")

    return Assessment(
        subject=subject,
        follow_up_questions=follow_ups,
        bright_line=bright_line,
        ratings=ratings,
        non_negotiable_title=non_negotiable_title,
        non_negotiable_citations=non_negotiable_citations,
        generated_at=now_utc(),
    )


def run(input_path: Path, principles_dir: Path, out_dir: Path) -> Path:
    raw = json.loads(input_path.read_text())
    assessment = build_assessment(raw, principles_dir)
    return write_report(assessment, out_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSON file with the assessment to validate and render — "
        "see .claude/skills/cst-finding/references/assessment-schema.md",
    )
    parser.add_argument("--principles-dir", type=Path, default=Path("principles"))
    parser.add_argument("--out-dir", type=Path, default=Path("eval/reports"))
    args = parser.parse_args(argv)

    try:
        path = run(args.input, args.principles_dir, args.out_dir)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Could not build assessment: {exc}", file=sys.stderr)
        return 1

    print(f"Advisory report written to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
