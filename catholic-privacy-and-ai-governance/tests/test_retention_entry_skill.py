"""Covers review-data-retention-entry's own metadata and end-to-end
behavior — the fifth task shape in this family (build-plan.md step 18),
deliberately the smallest: one entry, one verdict, no score, no deadline
list, no checklist.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "review-data-retention-entry"
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
        assert "gdpr-dpia" in ids
        assert "eu-ai-act" not in ids


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
            "title": "Parish bulletin subscriber list",
            "entry": {
                "description": "Email addresses and names collected via the sign-up form.",
                "category": "data element",
                "purpose": "Sending the weekly parish bulletin.",
                "last_reviewed_date": "2025-08-01",
            },
            "frameworks_considered": [
                {
                    "id": "gdpr-dpia",
                    "applicable": True,
                    "basis": "Some subscribers are EU residents.",
                }
            ],
            "verdict": {
                "action": "needs-review",
                "rationale": "No re-confirmation has happened in over a year despite "
                "the stated annual review policy.",
                "target_date": "2026-09-01",
            },
            "compliance": "Under GDPR Art. 5(1)(e), personal data must not be kept "
            "longer than necessary; the entry is overdue for its own stated review.",
            "cst_reflection": "Letting a review lapse quietly treats indefinite "
            "retention as the default, when the data is owed an active justification.",
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
        assert "Parish bulletin subscriber list" in text
        assert "2026-09-01" in text
        assert text.index("## Compliance") < text.index("## Catholic Social Teaching reflection")

    def test_unknown_framework_id_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_entry()
        broken["frameworks_considered"][0]["id"] = "not-a-real-framework"
        input_path = tmp_path / "entry.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "not-a-real-framework" in result.stderr

    def test_ai_governance_framework_id_is_rejected_here(self, tmp_path: Path) -> None:
        broken = self._valid_entry()
        broken["frameworks_considered"] = [{"id": "eu-ai-act", "applicable": True, "basis": "x"}]
        input_path = tmp_path / "entry.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "eu-ai-act" in result.stderr

    def test_needs_review_without_target_date_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_entry()
        broken["verdict"]["target_date"] = None
        input_path = tmp_path / "entry.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "target_date" in result.stderr

    def test_current_verdict_with_no_target_date_is_accepted(self, tmp_path: Path) -> None:
        entry = self._valid_entry()
        entry["verdict"] = {
            "action": "current",
            "rationale": "Reviewed six months ago and retention remains justified.",
            "target_date": None,
        }
        input_path = tmp_path / "entry.json"
        input_path.write_text(json.dumps(entry))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 0, result.stderr

    def test_cst_vocabulary_in_compliance_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_entry()
        broken["compliance"] = "In solidarity with parishioners, review this now."
        input_path = tmp_path / "entry.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "solidarity" in result.stderr
