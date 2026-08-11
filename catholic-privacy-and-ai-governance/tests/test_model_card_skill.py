"""Covers draft-model-card's own metadata and end-to-end behavior — build
sequence step 17, the AI-governance domain's second skill sharing
assess-ai-system-risk-tier's exact rubric and framework registry, the
same way draft-privacy-notice-update shares draft-privacy-impact-
assessment's.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "draft-model-card"
SIBLING_DIR = REPO_ROOT / ".claude" / "skills" / "assess-ai-system-risk-tier"
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
        # Shares its sibling's exact rubric and framework registry — there's
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
        this_rubric = (SKILL_DIR / "references" / "rubric" / "ai-criteria.md").read_text()
        sibling_rubric = (SIBLING_DIR / "references" / "rubric" / "ai-criteria.md").read_text()
        assert this_rubric == sibling_rubric

    def test_bundled_frameworks_match_the_sibling_skills_ai_governance_set(self) -> None:
        this_index = json.loads(
            (SKILL_DIR / "references" / "frameworks" / "index.json").read_text()
        )
        sibling_index = json.loads(
            (SIBLING_DIR / "references" / "frameworks" / "index.json").read_text()
        )
        assert {r["id"] for r in this_index} == {r["id"] for r in sibling_index}

    def test_bundled_frameworks_include_iso_42001(self) -> None:
        index = json.loads((SKILL_DIR / "references" / "frameworks" / "index.json").read_text())
        ids = {record["id"] for record in index}
        assert "iso-42001" in ids


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
            "title": "Campus Parking Permit Waitlist Ranker",
            "subject": {
                "description": "A model that ranks waitlisted students for a limited "
                "number of campus parking permits based on commute distance, class "
                "schedule conflicts, and prior violations.",
                "purpose": "Fairly allocating a scarce number of parking permits.",
                "personal_data": [
                    "student ID",
                    "home address",
                    "class schedule",
                    "violation history",
                ],
                "systems": ["parking office ranking tool"],
                "recipients": ["parking office staff"],
                "retention": "Ranking inputs and outputs are kept for one academic year.",
                "institution_context": "A university parking office.",
            },
            "frameworks_considered": [
                {
                    "id": "iso-42001",
                    "applicable": True,
                    "basis": "The university has voluntarily adopted ISO/IEC 42001 to "
                    "structure its AI management system.",
                },
                {
                    "id": "eu-ai-act",
                    "applicable": False,
                    "basis": "A US university with no EU nexus; the AI Act's territorial "
                    "scope under Art. 2 is not met.",
                },
            ],
            "ratings": [
                rating("risk-classification"),
                rating("governance-and-accountability"),
                rating("data-governance"),
                rating("transparency-and-documentation"),
                rating("accuracy-robustness-security"),
                rating("bias-and-fairness"),
                rating("human-oversight"),
            ],
            "compliance": "Under ISO/IEC 42001 Annex A.8, interested parties must be "
            "given information sufficient to understand the ranking model's intended "
            "purpose and known limitations before it is relied on for permit decisions.",
            "cst_reflection": "A waitlisted student is owed a documented, honest "
            "account of how the ranking works, not a black box they're told to trust.",
        }

    def test_valid_assessment_renders_a_report(self, tmp_path: Path) -> None:
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(self._valid_assessment()))
        out_dir = tmp_path / "reports"

        result = self._run(input_path, out_dir)

        assert result.returncode == 0, result.stderr
        rendered = list(out_dir.glob("*.md"))
        assert len(rendered) == 1
        assert "Campus Parking Permit Waitlist Ranker" in rendered[0].read_text()

    def test_privacy_dimension_id_is_rejected_here(self, tmp_path: Path) -> None:
        broken = self._valid_assessment()
        broken["ratings"][0]["dimension_id"] = "necessity-and-proportionality"
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "necessity-and-proportionality" in result.stderr
