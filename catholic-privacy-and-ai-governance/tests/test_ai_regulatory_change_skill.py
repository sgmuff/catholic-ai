"""Covers map-ai-regulatory-change's own metadata and end-to-end
behavior — the AI-governance domain's regulatory-change-shaped skill
(build-plan.md step 18), built by reusing map-regulatory-change's shape
directly rather than designing a third one.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "map-ai-regulatory-change"
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

    def test_regulatory_change_py_code_is_identical_to_the_privacy_siblings_own_copy(
        self,
    ) -> None:
        sibling = (
            REPO_ROOT
            / ".claude"
            / "skills"
            / "map-regulatory-change"
            / "scripts"
            / "regulatory_change.py"
        )

        def normalized_code(path: Path) -> str:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    node.value = ""
            return ast.unparse(tree)

        assert normalized_code(SCRIPTS_DIR / "regulatory_change.py") == normalized_code(sibling)


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

    def test_bundled_frameworks_are_ai_governance_only(self) -> None:
        index = json.loads((SKILL_DIR / "references" / "frameworks" / "index.json").read_text())
        ids = {record["id"] for record in index}
        assert {"eu-ai-act", "nist-ai-rmf"} <= ids
        assert "ccpa-cpra" not in ids


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
            "title": "EU AI Act serious-incident reporting portal opens",
            "development": {
                "source": "European Commission",
                "citation": "Implementing Regulation on Art. 73 reporting procedures",
                "summary": "A centralized reporting portal now handles Art. 73 "
                "serious-incident submissions, replacing direct notification to "
                "each Member State's market surveillance authority.",
                "published_date": "2026-03-01",
            },
            "frameworks_considered": [
                {
                    "id": "eu-ai-act",
                    "impacted": True,
                    "basis": "The registered Art. 73 reporting-obligation element "
                    "describes notifying the market surveillance authority directly; "
                    "the procedural mechanism has changed even though the deadlines "
                    "themselves have not.",
                },
                {
                    "id": "nist-ai-rmf",
                    "impacted": False,
                    "basis": "A voluntary US framework with no EU procedural dependency.",
                },
            ],
            "recommended_actions": [
                {
                    "id": "update-serious-incident-element",
                    "type": "update-required-element",
                    "framework_id": "eu-ai-act",
                    "description": "Update the serious-incident-reporting element to "
                    "reference the centralized portal as the submission mechanism.",
                }
            ],
            "compliance": "Under the Art. 73 implementing regulation, submissions "
            "must now be made through the centralized portal rather than directly "
            "to a Member State authority.",
            "cst_reflection": "Keeping the registry current keeps the reporting "
            "guidance this project gives an institution actually usable.",
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
        assert "EU AI Act serious-incident reporting portal opens" in text

    def test_privacy_framework_id_is_rejected_here(self, tmp_path: Path) -> None:
        broken = self._valid_change()
        broken["recommended_actions"][0]["framework_id"] = "ccpa-cpra"
        input_path = tmp_path / "change.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "ccpa-cpra" in result.stderr

    def test_register_new_framework_with_a_framework_id_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_change()
        broken["recommended_actions"] = [
            {
                "id": "register-new-standard",
                "type": "register-new-framework",
                "framework_id": "eu-ai-act",
                "description": "Should not reference an existing id.",
            }
        ]
        input_path = tmp_path / "change.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "framework_id" in result.stderr

    def test_cst_vocabulary_in_compliance_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_change()
        broken["compliance"] = "In solidarity with affected students, update this."
        input_path = tmp_path / "change.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "solidarity" in result.stderr
