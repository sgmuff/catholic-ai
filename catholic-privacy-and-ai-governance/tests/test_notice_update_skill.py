"""Covers draft-privacy-notice-update's own metadata and end-to-end
behavior — built at build sequence step 12 to prove a second skill can
share the same domain and the same rubric as its sibling without any
special-casing in the sync or validation machinery.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "draft-privacy-notice-update"
SIBLING_DIR = REPO_ROOT / ".claude" / "skills" / "draft-privacy-impact-assessment"
SCRIPTS_DIR = SKILL_DIR / "scripts"


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None and node.level == 0:
            names.add(node.module.split(".")[0])
    return names


class TestScriptsAreDependencyFree:
    def test_every_script_only_imports_stdlib_or_sibling_modules(self) -> None:
        sibling_modules = {p.stem for p in SCRIPTS_DIR.glob("*.py")}
        stdlib = set(sys.stdlib_module_names)
        for path in SCRIPTS_DIR.glob("*.py"):
            imported = _top_level_imports(path)
            disallowed = imported - stdlib - sibling_modules
            assert not disallowed, f"{path.name} imports non-stdlib module(s): {disallowed}"

    def test_every_script_is_byte_identical_to_the_sibling_skills_copy(self) -> None:
        # Unlike assess-ai-system-risk-tier (a different domain, so only
        # structurally identical modulo the docstring), this skill shares
        # its sibling's exact rubric and framework registry — there's
        # nothing domain-specific to differ, so every file should match
        # byte-for-byte.
        for path in SCRIPTS_DIR.glob("*.py"):
            sibling_path = SIBLING_DIR / "scripts" / path.name
            assert path.read_text() == sibling_path.read_text(), f"{path.name} diverged"


class TestSkillMetadata:
    def _frontmatter(self) -> dict:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        _, front, _ = text.split("---", 2)
        return yaml.safe_load(front)

    def test_name_matches_the_containing_folder(self) -> None:
        assert self._frontmatter()["name"] == SKILL_DIR.name

    def test_description_is_present_and_within_the_spec_limit(self) -> None:
        description = self._frontmatter()["description"]
        assert description.strip()
        assert len(description) <= 1024

    def test_plugin_json_name_matches_the_skill(self) -> None:
        plugin = json.loads((SKILL_DIR / ".claude-plugin" / "plugin.json").read_text())
        assert plugin["name"] == SKILL_DIR.name

    def test_bundled_rubric_matches_the_sibling_skills_exactly(self) -> None:
        this_rubric = (SKILL_DIR / "references" / "rubric" / "criteria.md").read_text()
        sibling_rubric = (SIBLING_DIR / "references" / "rubric" / "criteria.md").read_text()
        assert this_rubric == sibling_rubric

    def test_bundled_frameworks_match_the_sibling_skills_privacy_set(self) -> None:
        this_index = json.loads(
            (SKILL_DIR / "references" / "frameworks" / "index.json").read_text()
        )
        sibling_index = json.loads(
            (SIBLING_DIR / "references" / "frameworks" / "index.json").read_text()
        )
        assert {r["id"] for r in this_index} == {r["id"] for r in sibling_index}


class TestEndToEnd:
    """Runs the skill's own scripts/assessment.py as a subprocess, exactly
    how SKILL.md step 4 instructs the model to invoke it.
    """

    def _run(self, input_path: Path, out_dir: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "assessment.py"),
                "--input",
                str(input_path),
                "--out-dir",
                str(out_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def _valid_assessment(self) -> dict:
        def rating(dim: str, score: int = 5) -> dict:
            return {
                "dimension_id": dim,
                "score": score,
                "rationale": f"A grounded, specific rationale for {dim}.",
                "mitigation": None if score >= 4 else f"A concrete mitigation for {dim}.",
                "ideal": f"The fuller ideal for {dim}.",
                "contested": False,
            }

        return {
            "title": "Adding SMS Appointment Reminders",
            "subject": {
                "description": "A clinic is adding SMS text reminders for upcoming "
                "appointments, in addition to existing email reminders.",
                "purpose": "Reducing missed appointments.",
                "personal_data": ["patient name", "phone number", "appointment time"],
                "systems": ["SMS gateway vendor"],
                "recipients": ["SMS gateway vendor (processor)"],
                "retention": "Message logs kept 90 days, then deleted.",
                "institution_context": "A US medical clinic.",
            },
            "frameworks_considered": [
                {
                    "id": "hipaa",
                    "applicable": True,
                    "basis": "Appointment times and phone numbers tied to patient "
                    "identity are PHI.",
                }
            ],
            "ratings": [
                rating("necessity-and-proportionality"),
                rating("data-minimization"),
                rating("lawful-basis-and-consent"),
                rating("retention"),
                rating("security-controls"),
                rating("third-party-sharing"),
                rating("human-oversight"),
            ],
            "compliance": "Under 45 CFR 164.502(b), the SMS reminder content should be "
            "limited to appointment logistics and avoid disclosing visit reason in "
            "the message body itself, consistent with the minimum necessary standard.",
            "cst_reflection": "A reminder meant to help a patient keep an appointment "
            "shouldn't become a new way their health information travels further than "
            "the visit itself requires.",
        }

    def test_valid_assessment_renders_a_report(self, tmp_path: Path) -> None:
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(self._valid_assessment()))
        out_dir = tmp_path / "reports"

        result = self._run(input_path, out_dir)

        assert result.returncode == 0, result.stderr
        rendered = list(out_dir.glob("*.md"))
        assert len(rendered) == 1
        assert "Adding SMS Appointment Reminders" in rendered[0].read_text()

    def test_ai_governance_dimension_id_is_rejected_here(self, tmp_path: Path) -> None:
        # Confirms this skill's own bundled rubric is the privacy one, not
        # a stray copy of the AI-governance rubric — even though both are
        # synced by the same sync_all() call in the same run.
        broken = self._valid_assessment()
        broken["ratings"][0]["dimension_id"] = "risk-classification"
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "risk-classification" in result.stderr
