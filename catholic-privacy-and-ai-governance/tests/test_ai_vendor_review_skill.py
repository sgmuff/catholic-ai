"""Covers review-ai-vendor-governance's own metadata and end-to-end
behavior — the AI-governance domain's review-shaped skill (build-plan.md
step 16), built by reusing review-vendor-privacy-assessment's shape
directly rather than designing a third one, mirroring how
assess-ai-system-risk-tier and triage-ai-incident reused their own
privacy-domain siblings' shapes at steps 11 and 15.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "review-ai-vendor-governance"
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

    def test_review_py_code_is_identical_to_the_privacy_siblings_own_copy(self) -> None:
        # The whole point of reusing the review shape directly (step 16)
        # is that the validation logic never needs to diverge between
        # domains — only the module docstring and the argparse description
        # string name the domain.
        sibling = (
            REPO_ROOT
            / ".claude"
            / "skills"
            / "review-vendor-privacy-assessment"
            / "scripts"
            / "review.py"
        )

        def normalized_code(path: Path) -> str:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    node.value = ""
            return ast.unparse(tree)

        assert normalized_code(SCRIPTS_DIR / "review.py") == normalized_code(sibling)


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

    def test_bundled_baseline_is_the_ai_governance_one(self) -> None:
        baseline_files = list((SKILL_DIR / "references" / "baseline").glob("*.md"))
        assert [p.name for p in baseline_files] == ["ai-vendor.md"]

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
            "title": "Annual review of ParishRank AI, LLC",
            "vendor": {
                "name": "ParishRank AI, LLC",
                "description": "A vendor supplying a waitlist-ranking model the parking "
                "office uses to allocate a limited number of campus parking permits.",
                "service_provided": "Waitlist ranking model, hosted API.",
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
                    "basis": "The university has adopted the NIST AI RMF for its own "
                    "vendor AI governance diligence.",
                },
            ],
            "baseline_items": [
                {
                    "id": "model-documentation-provided",
                    "status": "satisfied",
                    "evidence": "Vendor-provided model card describing intended use and "
                    "known limitations.",
                    "gap": None,
                },
                {
                    "id": "evaluation-results-provided",
                    "status": "partial",
                    "evidence": "Accuracy benchmark provided; no bias/fairness evaluation.",
                    "gap": "No disparate-impact testing across student demographic groups "
                    "has been provided.",
                },
                {
                    "id": "incident-reporting-commitment",
                    "status": "satisfied",
                    "evidence": "Contract Section 9 commits to notice within 5 business days.",
                    "gap": None,
                },
                {
                    "id": "upstream-dependency-disclosure",
                    "status": "missing",
                    "evidence": None,
                    "gap": "Vendor has not disclosed which third-party model this ranking "
                    "tool is built on top of.",
                },
                {
                    "id": "human-oversight-support",
                    "status": "satisfied",
                    "evidence": "API exposes a per-ranking confidence score and supports "
                    "manual override before permits are issued.",
                    "gap": None,
                },
                {
                    "id": "update-notification-commitment",
                    "status": "satisfied",
                    "evidence": "Contract Section 9 commits to 30 days' notice before a "
                    "material model update.",
                    "gap": None,
                },
                {
                    "id": "data-governance-evidence",
                    "status": "satisfied",
                    "evidence": "Vendor's data processing addendum states university data "
                    "is not used to train models for other customers.",
                    "gap": None,
                },
            ],
            "remediation_commitments": [
                {
                    "id": "bias-testing",
                    "description": "Vendor to provide disparate-impact testing results.",
                    "target_date": "2026-10-01",
                    "status": "open",
                }
            ],
            "reassessment_due": "2027-08-01",
            "overall_risk": {
                "level": "moderate",
                "rationale": "Two baseline items unmet or partial (bias testing, upstream "
                "dependency disclosure), but human-oversight support is solid and a "
                "remediation commitment with a near-term date is in place.",
            },
            "compliance": "Under the NIST AI RMF's MEASURE function, the ranking model's "
            "outputs should be tested for disparate impact across student demographic "
            "groups before the vendor relationship continues past the remediation date.",
            "cst_reflection": "A waitlisted student is owed a system whose fairness has "
            "actually been checked, not merely a vendor's assurance that it probably is.",
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
        assert "ParishRank AI, LLC" in text
        assert "moderate" in text.lower()
        assert text.index("## Compliance") < text.index("## Catholic Social Teaching reflection")

    def test_missing_baseline_item_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_review()
        broken["baseline_items"] = broken["baseline_items"][:-1]
        input_path = tmp_path / "review.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "data-governance-evidence" in result.stderr

    def test_privacy_baseline_item_is_rejected_here(self, tmp_path: Path) -> None:
        broken = self._valid_review()
        broken["baseline_items"][0]["id"] = "dpa-in-place"
        input_path = tmp_path / "review.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "dpa-in-place" in result.stderr

    def test_missing_status_without_gap_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_review()
        broken["baseline_items"][3]["gap"] = None  # upstream-dependency-disclosure, missing
        input_path = tmp_path / "review.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "gap" in result.stderr

    def test_cst_vocabulary_in_compliance_is_rejected(self, tmp_path: Path) -> None:
        broken = self._valid_review()
        broken["compliance"] = "In solidarity with affected students, test for bias."
        input_path = tmp_path / "review.json"
        input_path.write_text(json.dumps(broken))

        result = self._run(input_path, tmp_path / "reports")

        assert result.returncode == 1
        assert "solidarity" in result.stderr
