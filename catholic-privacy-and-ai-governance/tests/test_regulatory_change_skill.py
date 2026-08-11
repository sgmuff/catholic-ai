"""Covers map-regulatory-change's own metadata and end-to-end behavior —
the sixth task shape in this family (build-plan.md step 18): unlike every
other skill, it doesn't evaluate an institution's own activity, system,
vendor, or inventory entry — it maps an external development's impact
against this project's own framework registry.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "map-regulatory-change"
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

    def test_no_rubric_or_baseline_module_or_directory_is_bundled(self) -> None:
        assert not (SCRIPTS_DIR / "rubric.py").exists()
        assert not (SCRIPTS_DIR / "baseline.py").exists()
        assert not (SKILL_DIR / "references" / "rubric").exists()
        assert not (SKILL_DIR / "references" / "baseline").exists()


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

    def test_bundled_frameworks_are_privacy_only(self) -> None:
        index = json.loads((SKILL_DIR / "references" / "frameworks" / "index.json").read_text())
        ids = {record["id"] for record in index}
        assert "ccpa-cpra" in ids
        assert "eu-ai-act" not in ids


class TestEndToEnd:
    def _run(self, input_path: Path, out_dir: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "regulatory_change.py"),
                "--input",
                str(input_path),
                "--out-dir",
                str(out_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def _valid_change(self) -> dict:
        return {
            "title": "CPPA risk-assessment regulations take effect",
            "development": {
                "source": "California Privacy Protection Agency",
                "citation": "Cal. Code Regs. tit. 11, §§ 7150-7157",
                "summary": "New regulations requiring a documented risk assessment "
                "before processing that presents significant risk to consumers.",
                "published_date": "2026-01-01",
            },
            "frameworks_considered": [
                {
                    "id": "ccpa-cpra",
                    "impacted": True,
                    "basis": "This registry entry already cites the risk-assessment "
                    "provision the new regulations flesh out with specific content "
                    "requirements.",
                },
                {
                    "id": "gdpr-dpia",
                    "impacted": False,
                    "basis": "A California-specific regulation with no bearing on "
                    "GDPR's own Art. 35 impact-assessment requirement.",
                },
            ],
            "recommended_actions": [
                {
                    "id": "update-risk-assessment-element",
                    "type": "update-required-element",
                    "framework_id": "ccpa-cpra",
                    "description": "Update the risk-assessment required element with "
                    "the regulations' specific content requirements.",
                }
            ],
            "compliance": "Under Cal. Code Regs. tit. 11, § 7152, a business must "
            "document specified elements in its risk assessment before conducting "
            "the processing.",
            "cst_reflection": "Keeping the registry current is how the assessment a "
            "parishioner's data receives stays honest, not stale.",
        }

    def test_valid_change_renders_a_report(self, tmp_path: Path) -> None:
        input_path = tmp_path / "change.json"
        input_path.write_text(json.dumps(self._valid_change()))
        out_dir = tmp_path / "reports"

        result = self._run(input_path, out_dir)

        assert result.returncode == 0, result.stderr
        rendered = list(out_dir.glob("*.md"))
        assert len(rendered) == 1
        text = rendered[0].read_text()
        assert "CPPA risk-assessment regulations take effect" in text
        assert text.index("## Compliance") < text.index("## Catholic Social Teaching reflection")

    def test_unknown_framework_id_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_change()
        broken["frameworks_considered"][0]["id"] = "not-a-real-framework"
        input_path = tmp_path / "change.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "not-a-real-framework" in result.stderr

    def test_ai_governance_framework_id_is_rejected_here(self, tmp_path: Path) -> None:
        broken = self._valid_change()
        broken["recommended_actions"][0]["framework_id"] = "eu-ai-act"
        input_path = tmp_path / "change.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "eu-ai-act" in result.stderr

    def test_empty_recommended_actions_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_change()
        broken["recommended_actions"] = []
        input_path = tmp_path / "change.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "recommended_actions" in result.stderr

    def test_no_action_type_renders_cleanly(self, tmp_path: Path) -> None:
        change = self._valid_change()
        change["recommended_actions"] = [
            {
                "id": "no-change-needed",
                "type": "no-action",
                "framework_id": None,
                "description": "Already fully reflected in the current registry entry.",
            }
        ]
        input_path = tmp_path / "change.json"
        input_path.write_text(json.dumps(change))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 0, result.stderr

    def test_cst_vocabulary_in_compliance_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_change()
        broken["compliance"] = "In solidarity with parishioners, update this element."
        input_path = tmp_path / "change.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "solidarity" in result.stderr
