"""Covers review-ai-system-reassessment's own metadata and end-to-end
behavior — the AI-governance domain's retention/verdict-shaped skill
(build-plan.md step 18), built by reusing review-data-retention-entry's
shape directly rather than designing a third one.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "review-ai-system-reassessment"
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

    def test_retention_py_code_is_identical_to_the_privacy_siblings_own_copy(self) -> None:
        # Only the module docstring, the argparse description, the
        # exception class's error-message strings, and the CLI's
        # FileNotFoundError message differ between domains — normalized
        # out here, so what's left must be structurally identical.
        sibling = (
            REPO_ROOT
            / ".claude"
            / "skills"
            / "review-data-retention-entry"
            / "scripts"
            / "retention.py"
        )

        def normalized_code(path: Path) -> str:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    node.value = ""
            return ast.unparse(tree)

        assert normalized_code(SCRIPTS_DIR / "retention.py") == normalized_code(sibling)


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
        assert "gdpr-dpia" not in ids


class TestEndToEnd:
    def _run(self, input_path: Path, out_dir: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "retention.py"),
                "--input",
                str(input_path),
                "--out-dir",
                str(out_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def _valid_entry(self) -> dict:
        return {
            "title": "Campus Parking Permit Waitlist Ranker",
            "entry": {
                "description": "A model ranking waitlisted students for a limited "
                "number of campus parking permits.",
                "category": "AI system",
                "purpose": "Fairly allocating a scarce number of parking permits.",
                "last_reviewed_date": "2025-02-01",
            },
            "frameworks_considered": [
                {
                    "id": "nist-ai-rmf",
                    "applicable": True,
                    "basis": "The university has adopted the NIST AI RMF for its own "
                    "TEVV practices.",
                }
            ],
            "verdict": {
                "action": "needs-review",
                "rationale": "The system's own annual re-evaluation interval lapsed "
                "six months ago with no re-run evaluation on file.",
                "target_date": "2026-09-01",
            },
            "compliance": "Under the NIST AI RMF's MEASURE function, TEVV results "
            "more than a year old no longer support a current fitness determination.",
            "cst_reflection": "A student relying on this ranking is owed a system "
            "whose fitness is actively confirmed, not assumed from a stale evaluation.",
        }

    def test_valid_entry_renders_a_report(self, tmp_path: Path) -> None:
        input_path = tmp_path / "entry.json"
        input_path.write_text(json.dumps(self._valid_entry()))
        out_dir = tmp_path / "reports"

        result = self._run(input_path, out_dir)

        assert result.returncode == 0, result.stderr
        rendered = list(out_dir.glob("*.md"))
        assert len(rendered) == 1
        text = rendered[0].read_text()
        assert "Campus Parking Permit Waitlist Ranker" in text
        assert "2026-09-01" in text

    def test_privacy_framework_id_is_rejected_here(self, tmp_path: Path) -> None:
        broken = self._valid_entry()
        broken["frameworks_considered"] = [{"id": "gdpr-dpia", "applicable": True, "basis": "x"}]
        input_path = tmp_path / "entry.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "gdpr-dpia" in result.stderr

    def test_invalid_verdict_action_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_entry()
        broken["verdict"]["action"] = "shrug"
        input_path = tmp_path / "entry.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "verdict.action" in result.stderr

    def test_cst_vocabulary_in_compliance_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_entry()
        broken["compliance"] = "In solidarity with students, re-run the evaluation."
        input_path = tmp_path / "entry.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "solidarity" in result.stderr
