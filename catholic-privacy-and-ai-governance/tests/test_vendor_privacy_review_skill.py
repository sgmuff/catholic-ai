"""Covers review-vendor-privacy-assessment's own metadata and end-to-end
behavior — the fourth task shape in this family (build-plan.md step 16):
a per-item satisfied/partial/missing baseline check, distinct from the
rubric-scored, single-deadline, and parallel-notification-obligation
shapes already built.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "review-vendor-privacy-assessment"
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

    def test_has_a_baseline_module_but_no_rubric_module_or_directory(self) -> None:
        assert (SCRIPTS_DIR / "baseline.py").exists()
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

    def test_bundled_baseline_is_the_privacy_one(self) -> None:
        baseline_files = list((SKILL_DIR / "references" / "baseline").glob("*.md"))
        assert [p.name for p in baseline_files] == ["privacy-vendor.md"]

    def test_bundled_frameworks_are_privacy_only(self) -> None:
        index = json.loads((SKILL_DIR / "references" / "frameworks" / "index.json").read_text())
        ids = {record["id"] for record in index}
        assert "gdpr-dpia" in ids
        assert "eu-ai-act" not in ids and "nist-ai-rmf" not in ids


class TestEndToEnd:
    """Runs the skill's own scripts/review.py as a subprocess, exactly how
    SKILL.md step 4 instructs the model to invoke it.
    """

    def _run(self, input_path: Path, out_dir: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "review.py"),
                "--input",
                str(input_path),
                "--out-dir",
                str(out_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def _valid_review(self) -> dict:
        return {
            "title": "Annual review of MailerParish, Inc.",
            "vendor": {
                "name": "MailerParish, Inc.",
                "description": "A bulk-email vendor the parish office uses to send the "
                "weekly bulletin to subscribed parishioners.",
                "service_provided": "Bulk email delivery and subscriber list hosting.",
            },
            "frameworks_considered": [
                {
                    "id": "gdpr-dpia",
                    "applicable": True,
                    "basis": "Some subscribed parishioners are EU residents.",
                },
                {
                    "id": "ccpa-cpra",
                    "applicable": False,
                    "basis": "The parish is not a business under CCPA/CPRA.",
                },
            ],
            "baseline_items": [
                {
                    "id": "dpa-in-place",
                    "status": "satisfied",
                    "evidence": "Signed DPA on file, executed 2025-01-10.",
                    "gap": None,
                },
                {
                    "id": "sub-processor-disclosure",
                    "status": "satisfied",
                    "evidence": "Sub-processor list disclosed in DPA Annex 2.",
                    "gap": None,
                },
                {
                    "id": "security-controls-evidence",
                    "status": "missing",
                    "evidence": None,
                    "gap": "No current SOC 2 report or completed questionnaire on file.",
                },
                {
                    "id": "breach-notification-commitment",
                    "status": "satisfied",
                    "evidence": "DPA Section 6 commits to notice within 48 hours.",
                    "gap": None,
                },
                {
                    "id": "data-return-deletion",
                    "status": "satisfied",
                    "evidence": "DPA Section 8 commits to deletion within 30 days of termination.",
                    "gap": None,
                },
                {
                    "id": "audit-rights",
                    "status": "partial",
                    "evidence": "DPA references a right to request an audit report.",
                    "gap": "No independent audit right, only a request for the vendor's own report.",
                },
                {
                    "id": "data-transfer-mechanism",
                    "status": "satisfied",
                    "evidence": "DPA Annex 3 references Standard Contractual Clauses.",
                    "gap": None,
                },
                {
                    "id": "minimum-necessary-scope",
                    "status": "satisfied",
                    "evidence": "Vendor access is scoped to the bulletin subscriber list only.",
                    "gap": None,
                },
            ],
            "remediation_commitments": [
                {
                    "id": "security-questionnaire",
                    "description": "Vendor to provide an updated security questionnaire.",
                    "target_date": "2026-09-15",
                    "status": "open",
                }
            ],
            "reassessment_due": "2027-08-01",
            "overall_risk": {
                "level": "moderate",
                "rationale": "One baseline item unmet and one partial, but the vendor has "
                "an open remediation commitment with a near-term date.",
            },
            "compliance": "Under GDPR Art. 28(3), the processing terms must specify the "
            "subject matter and duration of processing; current security-control evidence "
            "is required before the relationship continues past the remediation date.",
            "cst_reflection": "Closing this gap keeps the parishioners' trust intact rather "
            "than delegating it away unexamined.",
        }

    def test_valid_review_renders_a_report(self, tmp_path: Path) -> None:
        input_path = tmp_path / "review.json"
        input_path.write_text(json.dumps(self._valid_review()))
        out_dir = tmp_path / "reports"

        result = self._run(input_path, out_dir)

        assert result.returncode == 0, result.stderr
        rendered = list(out_dir.glob("*.md"))
        assert len(rendered) == 1
        text = rendered[0].read_text()
        assert "MailerParish, Inc." in text
        assert "moderate" in text.lower()
        assert text.index("## Compliance") < text.index("## Catholic Social Teaching reflection")

    def test_missing_baseline_item_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_review()
        broken["baseline_items"] = broken["baseline_items"][:-1]
        input_path = tmp_path / "review.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "minimum-necessary-scope" in result.stderr

    def test_ai_governance_baseline_item_is_rejected_here(self, tmp_path: Path) -> None:
        broken = self._valid_review()
        broken["baseline_items"][0]["id"] = "model-documentation-provided"
        input_path = tmp_path / "review.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "model-documentation-provided" in result.stderr

    def test_satisfied_without_evidence_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_review()
        broken["baseline_items"][0]["evidence"] = None
        input_path = tmp_path / "review.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "evidence" in result.stderr

    def test_cst_vocabulary_in_compliance_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_review()
        broken["compliance"] = "In solidarity with parishioners, close this gap."
        input_path = tmp_path / "review.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "solidarity" in result.stderr
