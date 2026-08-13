"""Covers triage-privacy-rights-request's own metadata and end-to-end
behavior — the first triage-shaped skill in this family (build-plan.md step
12 continued), proving the shape designed in src/privacy_and_ai_governance/
triage.py and the rubric-less sync path both work for a real skill bundle,
not just in isolation.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "triage-privacy-rights-request"
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

    def test_no_rubric_module_or_rubric_directory_is_bundled(self) -> None:
        # This skill has no rubric to parse — bundling rubric.py or an
        # empty references/rubric/ would misleadingly suggest it scores
        # something.
        assert not (SCRIPTS_DIR / "rubric.py").exists()
        assert not (SKILL_DIR / "references" / "rubric").exists()


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
        assert "gdpr-data-subject-rights" in ids
        assert "eu-ai-act" not in ids and "nist-ai-rmf" not in ids


class TestEndToEnd:
    """Runs the skill's own scripts/triage.py as a subprocess, exactly how
    SKILL.md step 3 instructs the model to invoke it.
    """

    def _run(self, input_path: Path, out_dir: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "triage.py"),
                "--input",
                str(input_path),
                "--out-dir",
                str(out_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def _valid_triage(self) -> dict:
        return {
            "title": "Access request from a returning parishioner",
            "request": {
                "description": "A parishioner emailed the parish office asking for a copy "
                "of all personal data held about them.",
                "request_type": "access",
                "channel": "email",
                "received_date": "2026-08-01",
                "requester_context": "The data subject themselves, an EU-resident parishioner.",
            },
            "frameworks_considered": [
                {
                    "id": "gdpr-data-subject-rights",
                    "applicable": True,
                    "basis": "The parishioner is an EU resident and the parish is the "
                    "controller of their personal data.",
                },
                {
                    "id": "ccpa-cpra",
                    "applicable": False,
                    "basis": "The parish is not a business under CCPA/CPRA and the "
                    "parishioner is not a California resident.",
                },
            ],
            "governing_deadline": {
                "statutory": True,
                "framework_id": "gdpr-data-subject-rights",
                "citation": "Art. 12(3)",
                "response_due": "2026-09-01",
                "basis": "One month from the 2026-08-01 receipt date, per Art. 12(3).",
            },
            "gaps": [
                {
                    "id": "identity",
                    "description": "Identity not yet verified against parish records.",
                    "blocking": True,
                }
            ],
            "compliance": "Under Art. 15, the parish must provide confirmation of "
            "processing and a copy of the personal data held, once identity is verified.",
            "cst_reflection": "Responding promptly treats the request as owed, not optional.",
        }

    def test_valid_triage_renders_a_report(self, tmp_path: Path) -> None:
        input_path = tmp_path / "triage.json"
        input_path.write_text(json.dumps(self._valid_triage()))
        out_dir = tmp_path / "reports"

        result = self._run(input_path, out_dir)

        assert result.returncode == 0, result.stderr
        rendered = list(out_dir.glob("*.md"))
        assert len(rendered) == 1
        text = rendered[0].read_text()
        assert "Access request from a returning parishioner" in text
        assert "2026-09-01" in text
        assert text.index("## Compliance") < text.index("## Catholic Social Teaching reflection")

    def test_unknown_framework_id_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_triage()
        broken["frameworks_considered"][0]["id"] = "not-a-real-framework"
        input_path = tmp_path / "triage.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "not-a-real-framework" in result.stderr

    def test_ai_governance_framework_id_is_rejected_here(self, tmp_path: Path) -> None:
        broken = self._valid_triage()
        broken["frameworks_considered"] = [{"id": "eu-ai-act", "applicable": True, "basis": "x"}]
        broken["governing_deadline"]["framework_id"] = "eu-ai-act"
        input_path = tmp_path / "triage.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "eu-ai-act" in result.stderr

    def test_deadline_before_received_date_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_triage()
        broken["governing_deadline"]["response_due"] = "2026-07-01"  # before received_date
        input_path = tmp_path / "triage.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "response_due" in result.stderr

    def test_deadline_governed_by_an_inapplicable_framework_is_rejected(
        self, tmp_path: Path
    ) -> None:
        broken = self._valid_triage()
        broken["governing_deadline"]["framework_id"] = "ccpa-cpra"  # marked inapplicable above
        input_path = tmp_path / "triage.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "ccpa-cpra" in result.stderr

    def test_no_applicable_framework_renders_a_non_statutory_internal_target(
        self, tmp_path: Path
    ) -> None:
        # The case a US parish routinely hits: neither GDPR (no EU nexus)
        # nor CCPA/CPRA (not a business) applies, but the request still
        # needs a plainly-stated response target.
        triage = self._valid_triage()
        for framework in triage["frameworks_considered"]:
            framework["applicable"] = False
        triage["governing_deadline"] = {
            "statutory": False,
            "framework_id": None,
            "citation": "Internal target — no applicable framework imposes a deadline.",
            "response_due": "2026-08-31",
            "basis": "30 days from the 2026-08-01 receipt date, an internal practice "
            "target calibrated against HIPAA's 30-day period for comparable requests "
            "— HIPAA itself does not apply here.",
        }
        input_path = tmp_path / "triage.json"
        input_path.write_text(json.dumps(triage))
        out_dir = tmp_path / "reports"

        result = self._run(input_path, out_dir)

        assert result.returncode == 0, result.stderr
        rendered = next(iter(out_dir.glob("*.md"))).read_text()
        assert "No statutory deadline applies" in rendered
        assert "2026-08-31" in rendered

    def test_statutory_false_with_a_named_framework_id_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_triage()
        for framework in broken["frameworks_considered"]:
            framework["applicable"] = False
        broken["governing_deadline"]["statutory"] = False
        # framework_id left set from _valid_triage() — must be null when non-statutory.
        input_path = tmp_path / "triage.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "null" in result.stderr

    def test_statutory_false_rejected_when_a_framework_is_applicable(self, tmp_path: Path) -> None:
        broken = self._valid_triage()  # gdpr-data-subject-rights still applicable here
        broken["governing_deadline"]["statutory"] = False
        broken["governing_deadline"]["framework_id"] = None
        input_path = tmp_path / "triage.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "statutory" in result.stderr

    def test_cst_vocabulary_in_compliance_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_triage()
        broken["compliance"] = "In solidarity with the parishioner, a copy must be provided."
        input_path = tmp_path / "triage.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "solidarity" in result.stderr
