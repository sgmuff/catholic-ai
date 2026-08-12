"""Covers assess-ai-system-risk-tier's own metadata and end-to-end behavior
— the AI-governance domain's flagship, built at build sequence step 11 to
prove build-plan.md §3's pluggable-framework architecture actually
generalizes to a second domain, not just a second framework within one.
Mirrors tests/test_flagship_skill.py's structure deliberately, since
proving the two skills work the same way is the point of this step.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "assess-ai-system-risk-tier"
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

    def test_assessment_py_code_is_identical_to_the_flagships_own_copy(self) -> None:
        # The whole point of find_rubric_path() discovering its rubric file
        # by name (build sequence step 11) is that the actual logic never
        # needs to diverge between skills — only the module docstring and
        # the argparse description string name the domain. Compare the
        # parsed structure with those two string literals normalized out,
        # rather than diffing text (which the docstring wording would break).
        sibling = (
            REPO_ROOT
            / ".claude"
            / "skills"
            / "draft-privacy-impact-assessment"
            / "scripts"
            / "assessment.py"
        )

        def normalized_code(path: Path) -> str:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    node.value = ""
            return ast.unparse(tree)

        assert normalized_code(SCRIPTS_DIR / "assessment.py") == normalized_code(sibling)


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

    def test_bundled_rubric_is_the_ai_governance_one_not_the_privacy_one(self) -> None:
        rubric_files = list((SKILL_DIR / "references" / "rubric").glob("*.md"))
        assert [p.name for p in rubric_files] == ["ai-criteria.md"]

    def test_bundled_frameworks_are_ai_governance_only(self) -> None:
        # Asserted by membership, not exact count — the AI-governance
        # framework set grows independently of this skill (e.g. iso-42001,
        # added at build sequence step 17), and every skill in the domain
        # picks up a new entry the next sync, per build-plan.md §3.
        index = json.loads((SKILL_DIR / "references" / "frameworks" / "index.json").read_text())
        ids = {record["id"] for record in index}
        assert {"eu-ai-act", "nist-ai-rmf"} <= ids
        assert "gdpr-dpia" not in ids and "hipaa" not in ids


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
                "description": "A university parking office uses a model to rank waitlisted "
                "students for a limited number of campus parking permits based on "
                "commute distance, class schedule conflicts, and prior violations.",
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
                    "id": "eu-ai-act",
                    "applicable": False,
                    "basis": "A US university with no EU nexus; the AI Act's territorial "
                    "scope under Art. 2 is not met.",
                },
                {
                    "id": "nist-ai-rmf",
                    "applicable": True,
                    "basis": "The university has voluntarily adopted the NIST AI RMF to "
                    "structure its AI governance practices.",
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
            "compliance": "Under the NIST AI RMF's MEASURE function, the ranking model's "
            "outputs should be tested for disparate impact across student demographic "
            "groups before continued use.",
            "cst_reflection": "A waitlisted student is owed more than a score; the office's "
            "willingness to explain why a specific ranking was produced, and to correct it "
            "when it's wrong, is what keeps the ranking answerable to the student it affects.",
        }

    def test_valid_assessment_renders_a_report(self, tmp_path: Path) -> None:
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(self._valid_assessment()))
        out_dir = tmp_path / "reports"

        result = self._run(input_path, out_dir)

        assert result.returncode == 0, result.stderr
        rendered = list(out_dir.glob("*.md"))
        assert len(rendered) == 1
        text = rendered[0].read_text()
        assert "Campus Parking Permit Waitlist Ranker" in text
        assert text.index("## Catholic Social Teaching summary") < text.index("## Compliance")

    def test_unknown_dimension_from_the_privacy_rubric_is_rejected(self, tmp_path: Path) -> None:
        # A privacy-domain dimension id must not silently pass here — the
        # two rubrics are genuinely separate, not just renamed copies.
        broken = self._valid_assessment()
        broken["ratings"][0]["dimension_id"] = "necessity-and-proportionality"
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "necessity-and-proportionality" in result.stderr
        assert "risk-classification" in result.stderr  # reported missing

    def test_privacy_framework_id_is_rejected_here(self, tmp_path: Path) -> None:
        broken = self._valid_assessment()
        broken["frameworks_considered"] = [{"id": "gdpr-dpia", "applicable": True, "basis": "x"}]
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "gdpr-dpia" in result.stderr

    def test_cst_vocabulary_in_compliance_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_assessment()
        broken["compliance"] = "In solidarity with affected students, ranking must be tested."
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "solidarity" in result.stderr
