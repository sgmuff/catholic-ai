"""Covers triage-ai-incident's own metadata and end-to-end behavior — the
AI-governance domain's incident-triage skill (build-plan.md step 15),
built by reusing triage-privacy-incident's shape directly rather than
designing a third one, mirroring how assess-ai-system-risk-tier reused
draft-privacy-impact-assessment's rubric-scored shape at step 11.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "triage-ai-incident"
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

    def test_incident_py_code_is_identical_to_the_privacy_siblings_own_copy(self) -> None:
        # The whole point of reusing the incident shape directly (step 15)
        # is that the validation logic never needs to diverge between
        # domains — only the module docstring and the argparse description
        # string name the domain. Compare parsed structure with those two
        # string literals normalized out, rather than diffing text.
        sibling = (
            REPO_ROOT / ".claude" / "skills" / "triage-privacy-incident" / "scripts" / "incident.py"
        )

        def normalized_code(path: Path) -> str:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    node.value = ""
            return ast.unparse(tree)

        assert normalized_code(SCRIPTS_DIR / "incident.py") == normalized_code(sibling)


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
        # Asserted by membership, not exact count — the AI-governance
        # framework set grows independently of this skill (e.g. iso-42001,
        # added at build sequence step 17), and every skill in the domain
        # picks up a new entry the next sync, per build-plan.md §3.
        index = json.loads((SKILL_DIR / "references" / "frameworks" / "index.json").read_text())
        ids = {record["id"] for record in index}
        assert {"eu-ai-act", "nist-ai-rmf"} <= ids
        assert "gdpr-dpia" not in ids and "hipaa" not in ids


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
            "title": "Biased waitlist ranking after a data pipeline change",
            "incident": {
                "description": "A university's parking-permit waitlist ranking model began "
                "systematically down-ranking students from a specific residence hall after a "
                "pipeline change silently dropped a data field; staff relied on the ranking to "
                "deny permits for two weeks before the pattern was noticed.",
                "discovered_date": "2026-08-01",
                "affected_systems": ["parking office ranking tool"],
                "data_types": ["student ID", "home address", "ranking output"],
                "individuals_affected_estimate": 85,
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
                    "basis": "The university has adopted the NIST AI RMF to structure its "
                    "own AI incident response.",
                },
            ],
            "severity": {
                "level": "moderate",
                "rationale": "Concrete adverse impact (permit denial) affecting a bounded "
                "group of 85 students over two weeks, discovered and correctable, not an "
                "ongoing safety or infrastructure risk.",
            },
            "notification_obligations": [
                {
                    "id": "internal-governance-body",
                    "framework_id": "nist-ai-rmf",
                    "audience": "Internal AI governance committee",
                    "citation": "MANAGE",
                    "due_date": "2026-08-08",
                    "basis": "One week from the 2026-08-01 discovery date, per the "
                    "university's own adopted MANAGE-function incident-response target.",
                }
            ],
            "gaps": [
                {
                    "id": "affected-list",
                    "description": "Full list of denied students not yet cross-checked "
                    "against the pipeline defect window.",
                    "blocking": False,
                }
            ],
            "escalation": {
                "required": True,
                "rationale": "Concrete denial of a benefit to identifiable students meets "
                "the internal escalation threshold for AI governance review.",
            },
            "compliance": "Under the NIST AI RMF's MANAGE function, the affected ranking "
            "pipeline must be corrected and the denied permits reprocessed before the "
            "model resumes normal operation.",
            "cst_reflection": "A student denied a permit by a silent defect is owed a "
            "correction, not an explanation after the fact of why the error happened.",
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
        assert "Biased waitlist ranking after a data pipeline change" in text
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

    def test_privacy_framework_id_is_rejected_here(self, tmp_path: Path) -> None:
        broken = self._valid_incident()
        broken["frameworks_considered"] = [
            {"id": "ca-breach-notification", "applicable": True, "basis": "x"}
        ]
        broken["notification_obligations"][0]["framework_id"] = "ca-breach-notification"
        input_path = tmp_path / "incident.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "ca-breach-notification" in result.stderr

    def test_invalid_severity_level_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_incident()
        broken["severity"]["level"] = "catastrophic"
        input_path = tmp_path / "incident.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "severity.level" in result.stderr

    def test_eu_ai_act_serious_incident_deadline_scenario_renders(self, tmp_path: Path) -> None:
        # Exercises the EU AI Act framework specifically, not just the
        # generic incident shape — the 2-day widespread-infringement tier.
        scenario = self._valid_incident()
        scenario["frameworks_considered"][0]["applicable"] = True
        scenario["frameworks_considered"][0]["basis"] = (
            "The university has an EU-based branch campus using this system."
        )
        scenario["notification_obligations"].append(
            {
                "id": "eu-market-surveillance",
                "framework_id": "eu-ai-act",
                "audience": "EU market surveillance authority",
                "citation": "Art. 73(3)",
                "due_date": "2026-08-03",
                "basis": "Widespread infringement affecting 85 students — immediately, and "
                "no later than 2 days from the 2026-08-01 discovery, per Art. 73(3).",
            }
        )
        input_path = tmp_path / "incident.json"
        input_path.write_text(json.dumps(scenario))
        out_dir = tmp_path / "reports"

        result = self._run(input_path, out_dir)

        assert result.returncode == 0, result.stderr
        text = next(iter(out_dir.glob("*.md"))).read_text()
        assert "EU market surveillance authority" in text
        assert "Internal AI governance committee" in text

    def test_cst_vocabulary_in_compliance_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_incident()
        broken["compliance"] = "In solidarity with the affected students, correct the model."
        input_path = tmp_path / "incident.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "solidarity" in result.stderr
