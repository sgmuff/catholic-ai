"""Covers triage-privacy-incident's own metadata and end-to-end behavior —
the second triage-shaped skill in this family (build-plan.md step 14), a
sibling of triage-privacy-rights-request with a genuinely different inner
shape: several independent, simultaneous notification obligations rather
than one governing deadline.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "triage-privacy-incident"
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
        assert "gdpr-breach-notification" in ids
        assert "ca-breach-notification" in ids
        assert "eu-ai-act" not in ids and "nist-ai-rmf" not in ids


class TestEndToEnd:
    """Runs the skill's own scripts/incident.py as a subprocess, exactly
    how SKILL.md step 4 instructs the model to invoke it.
    """

    def _run(self, input_path: Path, out_dir: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "incident.py"),
                "--input",
                str(input_path),
                "--out-dir",
                str(out_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def _valid_incident(self) -> dict:
        return {
            "title": "Misdirected email containing parishioner records",
            "incident": {
                "description": "A parish office staff member emailed a spreadsheet of "
                "150 parishioners' names, addresses, and donation history to the wrong "
                "internal distribution list.",
                "discovered_date": "2026-08-01",
                "affected_systems": ["parish office email"],
                "data_types": ["name", "address", "donation history"],
                "individuals_affected_estimate": 150,
            },
            "frameworks_considered": [
                {
                    "id": "ca-breach-notification",
                    "applicable": True,
                    "basis": "Some affected parishioners are California residents.",
                },
                {
                    "id": "gdpr-breach-notification",
                    "applicable": False,
                    "basis": "No EU-resident parishioners are in the affected list.",
                },
            ],
            "severity": {
                "level": "moderate",
                "rationale": "Financial/donation data exposed to an unintended internal "
                "list, not a public or malicious external actor.",
            },
            "notification_obligations": [
                {
                    "id": "ca-residents",
                    "framework_id": "ca-breach-notification",
                    "audience": "Affected California residents",
                    "citation": "Civ. Code § 1798.82(a)(2)(A)",
                    "due_date": "2026-08-31",
                    "basis": "30 calendar days from the 2026-08-01 discovery date, per "
                    "Civ. Code § 1798.82(a)(2)(A).",
                }
            ],
            "gaps": [
                {
                    "id": "recipient-list",
                    "description": "Full list of unintended recipients not yet confirmed.",
                    "blocking": False,
                }
            ],
            "escalation": {
                "required": True,
                "rationale": "Meets the notification-obligation threshold for "
                "executive/legal awareness even though severity is moderate.",
            },
            "compliance": "Under Civ. Code § 1798.82(a)(2)(A), affected California "
            "residents must be notified within 30 calendar days of the 2026-08-01 "
            "discovery date.",
            "cst_reflection": "Treating the exposure as owed a prompt, honest accounting "
            "to those affected, not a risk to be managed quietly.",
        }

    def test_valid_incident_renders_a_report(self, tmp_path: Path) -> None:
        input_path = tmp_path / "incident.json"
        input_path.write_text(json.dumps(self._valid_incident()))
        out_dir = tmp_path / "reports"

        result = self._run(input_path, out_dir)

        assert result.returncode == 0, result.stderr
        rendered = list(out_dir.glob("*.md"))
        assert len(rendered) == 1
        text = rendered[0].read_text()
        assert "Misdirected email containing parishioner records" in text
        assert "2026-08-31" in text
        assert "moderate" in text.lower()
        assert text.index("## Compliance") < text.index("## Catholic Social Teaching reflection")

    def test_unknown_framework_id_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_incident()
        broken["frameworks_considered"][0]["id"] = "not-a-real-framework"
        input_path = tmp_path / "incident.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "not-a-real-framework" in result.stderr

    def test_ai_governance_framework_id_is_rejected_here(self, tmp_path: Path) -> None:
        broken = self._valid_incident()
        broken["frameworks_considered"] = [{"id": "eu-ai-act", "applicable": True, "basis": "x"}]
        broken["notification_obligations"][0]["framework_id"] = "eu-ai-act"
        input_path = tmp_path / "incident.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "eu-ai-act" in result.stderr

    def test_invalid_severity_level_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_incident()
        broken["severity"]["level"] = "catastrophic"
        input_path = tmp_path / "incident.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "severity.level" in result.stderr

    def test_obligation_due_date_before_discovered_date_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_incident()
        broken["notification_obligations"][0]["due_date"] = "2026-07-01"
        input_path = tmp_path / "incident.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "due_date" in result.stderr

    def test_obligation_governed_by_an_inapplicable_framework_is_rejected(
        self, tmp_path: Path
    ) -> None:
        broken = self._valid_incident()
        broken["notification_obligations"][0]["framework_id"] = "gdpr-breach-notification"
        input_path = tmp_path / "incident.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "gdpr-breach-notification" in result.stderr
        assert "applicable" in result.stderr

    def test_two_independent_notification_obligations_both_render(self, tmp_path: Path) -> None:
        multi = self._valid_incident()
        multi["frameworks_considered"][1]["applicable"] = True
        multi["frameworks_considered"][1]["basis"] = "Some affected parishioners are EU residents."
        multi["notification_obligations"].append(
            {
                "id": "eu-authority",
                "framework_id": "gdpr-breach-notification",
                "audience": "Competent supervisory authority",
                "citation": "Art. 33(1)",
                "due_date": "2026-08-04",
                "basis": "72 hours from the 2026-08-01 discovery, per Art. 33(1).",
            }
        )
        input_path = tmp_path / "incident.json"
        input_path.write_text(json.dumps(multi))
        out_dir = tmp_path / "reports"

        result = self._run(input_path, out_dir)

        assert result.returncode == 0, result.stderr
        text = next(iter(out_dir.glob("*.md"))).read_text()
        assert "Affected California residents" in text
        assert "Competent supervisory authority" in text

    def test_cst_vocabulary_in_compliance_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_incident()
        broken["compliance"] = "In solidarity with the parishioners, notify them promptly."
        input_path = tmp_path / "incident.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "solidarity" in result.stderr
