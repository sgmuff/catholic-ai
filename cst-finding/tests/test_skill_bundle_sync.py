"""Confirms the `cst-finding` skill's bundled copy under
`.claude/skills/cst-finding/{references,scripts}/` is exactly what
`eval/sync_skill_bundle.py` would produce from the real `principles/`,
`rubric/`, and `eval/` content in this checkout — not a fixture. A failure
here means someone edited the authored source without running
`make sync-skill-bundle`.
"""

from pathlib import Path

from eval.sync_skill_bundle import (
    PORTABLE_PRINCIPLES_SOURCE,
    assessment_module_bytes,
    non_negotiables_json_bytes,
    principles_json_bytes,
    report_module_bytes,
    rubric_bytes,
)

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SKILL_DIR = _REPO_ROOT / ".claude" / "skills" / "cst-finding"
_REFERENCES_DIR = _SKILL_DIR / "references"
_SCRIPTS_DIR = _SKILL_DIR / "scripts"

_MISMATCH = (
    "committed {name} is out of sync with the authored source — run `make sync-skill-bundle`"
)


def test_principles_json_is_synced() -> None:
    committed = (_REFERENCES_DIR / "principles.json").read_bytes()
    fresh = principles_json_bytes(_REPO_ROOT / "principles")
    assert committed == fresh, _MISMATCH.format(name="references/principles.json")


def test_non_negotiables_json_is_synced() -> None:
    committed = (_REFERENCES_DIR / "non-negotiables.json").read_bytes()
    fresh = non_negotiables_json_bytes(_REPO_ROOT / "principles")
    assert committed == fresh, _MISMATCH.format(name="references/non-negotiables.json")


def test_rubric_files_are_synced() -> None:
    for filename in ("criteria.md", "known-tensions.md"):
        committed = (_REFERENCES_DIR / "rubric" / filename).read_bytes()
        fresh = rubric_bytes(_REPO_ROOT / "rubric", filename)
        assert committed == fresh, _MISMATCH.format(name=f"references/rubric/{filename}")


def test_scripts_report_is_synced() -> None:
    committed = (_SCRIPTS_DIR / "report.py").read_bytes()
    fresh = report_module_bytes(_REPO_ROOT / "eval")
    assert committed == fresh, _MISMATCH.format(name="scripts/report.py")


def test_scripts_principles_is_synced() -> None:
    committed = (_SCRIPTS_DIR / "principles.py").read_bytes()
    assert committed == PORTABLE_PRINCIPLES_SOURCE.encode(), _MISMATCH.format(
        name="scripts/principles.py"
    )


def test_scripts_assessment_is_synced() -> None:
    committed = (_SCRIPTS_DIR / "assessment.py").read_bytes()
    fresh = assessment_module_bytes(_REPO_ROOT / "eval")
    assert committed == fresh, _MISMATCH.format(name="scripts/assessment.py")
