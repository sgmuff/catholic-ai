"""Covers the flagship skill's own build-plan.md requirements that aren't
about the source project's src/ package: that its bundled scripts/ are
genuinely dependency-free (docs/standards/skills.md's standalone-
distribution requirement), and that the skill actually works end-to-end as
installed, not just in the abstract.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "draft-privacy-impact-assessment"
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

    def test_scripts_directory_has_the_expected_files(self) -> None:
        names = {p.name for p in SCRIPTS_DIR.glob("*.py")}
        assert names == {"assessment.py", "concision.py", "language.py", "report.py", "rubric.py"}


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


class TestEndToEnd:
    """Runs the skill's own scripts/assessment.py as a subprocess, exactly
    how SKILL.md step 4 instructs the model to invoke it — not by importing
    it as a test helper, which could hide a bug the real invocation would hit.
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
            "title": "Parish Bulletin Sign-Up Form",
            "subject": {
                "description": "A web form collecting email addresses for a weekly bulletin.",
                "purpose": "Sending the weekly parish bulletin.",
                "personal_data": ["email address"],
                "systems": ["Mailchimp"],
                "recipients": ["parish office staff", "Mailchimp (processor)"],
                "retention": "Kept until the parishioner unsubscribes.",
                "institution_context": "A parish",
            },
            "frameworks_considered": [
                {
                    "id": "gdpr-dpia",
                    "applicable": True,
                    "basis": "Parish serves EU-resident parishioners.",
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
            "compliance": "Under GDPR Art. 35(7)(d), retention must be bounded and enforced.",
            "cst_reflection": "This keeps the parishioner's data tied to an active relationship.",
        }

    def test_valid_assessment_renders_a_report(self, tmp_path: Path) -> None:
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(self._valid_assessment()))
        out_dir = tmp_path / "reports"

        result = self._run(input_path, out_dir)

        assert result.returncode == 0, result.stderr
        rendered = list(out_dir.glob("*.md"))
        assert len(rendered) == 1
        assert "Parish Bulletin Sign-Up Form" in rendered[0].read_text()
        assert rendered[0].read_text().index("## Compliance") < rendered[0].read_text().index(
            "## Catholic Social Teaching reflection"
        )

    def test_missing_retention_and_unknown_framework_id_both_reported(self, tmp_path: Path) -> None:
        broken = self._valid_assessment()
        broken["subject"]["retention"] = ""
        broken["frameworks_considered"] = [
            {"id": "not-a-real-framework", "applicable": True, "basis": "x"}
        ]
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "subject.retention" in result.stderr
        assert "not-a-real-framework" in result.stderr

    def test_cst_vocabulary_in_compliance_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_assessment()
        broken["compliance"] = "In solidarity with data subjects, retention must be bounded."
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "solidarity" in result.stderr

    def test_overlong_field_triggers_a_non_fatal_warning_but_still_renders(
        self, tmp_path: Path
    ) -> None:
        padded = self._valid_assessment()
        padded["ratings"][0]["rationale"] = "word " * 500
        input_path = tmp_path / "assessment.json"
        input_path.write_text(json.dumps(padded))
        out_dir = tmp_path / "reports"

        result = self._run(input_path, out_dir)

        assert result.returncode == 0, result.stderr
        assert "warning" in result.stderr.lower()
        assert list(out_dir.glob("*.md"))
