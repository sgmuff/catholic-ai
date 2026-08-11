import json
import shutil
from pathlib import Path

import pytest
import yaml

from eval.sync_skill_bundle import (
    ManifestDriftError,
    render_family_manifest_markdown,
    render_frameworks_index_markdown,
    sync_all,
    sync_router_references,
    sync_skill_references,
    sync_skill_scripts,
)

REPO_ROOT = Path(__file__).parent.parent
REAL_FRAMEWORKS_DIR = REPO_ROOT / "frameworks"
REAL_RUBRIC_PATH = REPO_ROOT / "rubric" / "criteria.md"
REAL_SRC_DIR = REPO_ROOT / "src" / "privacy_and_ai_governance"
STDLIB_ONLY_MODULES = ["concision.py", "language.py", "report.py", "rubric.py"]


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def _framework_content(framework_id: str, name: str) -> dict:
    """A minimal but schema-complete framework content file — every field
    frameworks/schema.yaml actually requires, so it round-trips through the
    real loader and renderer the same way authored content does.
    """
    return {
        "id": framework_id,
        "name": name,
        "citation_root": name,
        "source_url": f"https://example.org/{framework_id}",
        "review_status": "unreviewed",
        "applicability": {"trigger": "A test trigger.", "jurisdiction": ["any"]},
        "required_elements": [{"id": "el-1", "citation": "§1", "requirement": "Do the thing."}],
        "terms_of_art": [{"term": "widget", "meaning": "A test term."}],
    }


class TestRenderFrameworksIndexMarkdown:
    def test_empty_list_says_nothing_is_registered(self) -> None:
        markdown = render_frameworks_index_markdown([])
        assert "no frameworks" in markdown.lower()

    def test_includes_the_fields_a_skill_needs_to_reason_about_applicability(self) -> None:
        record = {
            "id": "gdpr-dpia",
            "name": "GDPR Art. 35",
            "type": "law",
            "citation_root": "GDPR Art. 35",
            "review_status": "unreviewed",
            "source_url": "https://example.org/art-35",
            "applicability": {"trigger": "High risk processing", "jurisdiction": ["EU"]},
            "file": "privacy/gdpr-dpia.yaml",
        }
        markdown = render_frameworks_index_markdown([record])
        assert "gdpr-dpia" in markdown
        assert "law" in markdown
        assert "unreviewed" in markdown
        assert "High risk processing" in markdown
        assert "EU" in markdown


class TestSyncSkillReferences:
    def test_syncs_rubric_and_the_real_active_privacy_frameworks(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "draft-privacy-impact-assessment"
        written = sync_skill_references(skill_dir, "privacy", REAL_FRAMEWORKS_DIR, REAL_RUBRIC_PATH)

        rubric_dest = skill_dir / "references" / "rubric" / "criteria.md"
        assert rubric_dest in written
        assert rubric_dest.read_text() == REAL_RUBRIC_PATH.read_text()

        index_dest = skill_dir / "references" / "frameworks" / "index.md"
        assert "gdpr-dpia" in index_dest.read_text()

        content_dest = skill_dir / "references" / "frameworks" / "privacy" / "gdpr-dpia.yaml"
        assert content_dest in written
        assert (
            content_dest.read_text()
            == (REAL_FRAMEWORKS_DIR / "privacy" / "gdpr-dpia.yaml").read_text()
        )

    def test_writes_a_machine_readable_json_index_alongside_the_markdown_one(
        self, tmp_path: Path
    ) -> None:
        skill_dir = tmp_path / "draft-privacy-impact-assessment"
        written = sync_skill_references(skill_dir, "privacy", REAL_FRAMEWORKS_DIR, REAL_RUBRIC_PATH)

        json_dest = skill_dir / "references" / "frameworks" / "index.json"
        assert json_dest in written
        records = json.loads(json_dest.read_text())
        by_id = {r["id"]: r for r in records}
        assert "gdpr-dpia" in by_id  # the original entry never disappears as the registry grows
        assert by_id["gdpr-dpia"]["citation_root"] == "GDPR Art. 35"
        assert len(by_id["gdpr-dpia"]["required_elements"]) == 10

    def test_is_idempotent(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "draft-privacy-impact-assessment"
        first = sync_skill_references(skill_dir, "privacy", REAL_FRAMEWORKS_DIR, REAL_RUBRIC_PATH)
        contents_after_first = {p: p.read_text() for p in first}

        second = sync_skill_references(skill_dir, "privacy", REAL_FRAMEWORKS_DIR, REAL_RUBRIC_PATH)
        contents_after_second = {p: p.read_text() for p in second}

        assert contents_after_first == contents_after_second

    def test_excludes_frameworks_from_a_different_domain(self, tmp_path: Path) -> None:
        frameworks_dir = tmp_path / "frameworks"
        frameworks_dir.mkdir()
        shutil.copy(REAL_FRAMEWORKS_DIR / "schema.yaml", frameworks_dir / "schema.yaml")
        _write_yaml(
            frameworks_dir / "index.yaml",
            {
                "frameworks": [
                    {
                        "id": "privacy-one",
                        "name": "Privacy One",
                        "type": "law",
                        "domain": "privacy",
                        "file": "privacy/privacy-one.yaml",
                        "status": "active",
                    },
                    {
                        "id": "ai-one",
                        "name": "AI One",
                        "type": "law",
                        "domain": "ai-governance",
                        "file": "ai-governance/ai-one.yaml",
                        "status": "active",
                    },
                ]
            },
        )
        _write_yaml(
            frameworks_dir / "privacy" / "privacy-one.yaml",
            _framework_content("privacy-one", "Privacy One"),
        )
        _write_yaml(
            frameworks_dir / "ai-governance" / "ai-one.yaml",
            _framework_content("ai-one", "AI One"),
        )

        skill_dir = tmp_path / "some-privacy-skill"
        sync_skill_references(skill_dir, "privacy", frameworks_dir, REAL_RUBRIC_PATH)

        index_text = (skill_dir / "references" / "frameworks" / "index.md").read_text()
        assert "privacy-one" in index_text
        assert "ai-one" not in index_text
        assert not (skill_dir / "references" / "frameworks" / "ai-governance").exists()

    def test_rubric_path_none_skips_rubric_syncing_entirely(self, tmp_path: Path) -> None:
        # A triage-shaped skill (build sequence step 12) has no rubric at
        # all — sync_skill_references must not fail or write an empty
        # references/rubric/ directory for it.
        skill_dir = tmp_path / "triage-privacy-rights-request"
        written = sync_skill_references(skill_dir, "privacy", REAL_FRAMEWORKS_DIR, None)

        assert not (skill_dir / "references" / "rubric").exists()
        assert not any("rubric" in str(p.relative_to(skill_dir)) for p in written)
        assert (skill_dir / "references" / "frameworks" / "index.md").exists()


class TestSyncSkillScripts:
    """Covers build-plan.md §4/§6.2's standalone-distribution requirement:
    everything a skill runs must be a dependency-free, stdlib-only copy —
    never hand-maintained twice, never left to drift from the tested
    src/ modules it's copied from.
    """

    def test_copies_every_stdlib_only_module_byte_for_byte(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "draft-privacy-impact-assessment"
        written = sync_skill_scripts(skill_dir, REAL_SRC_DIR)

        for module in STDLIB_ONLY_MODULES:
            dest = skill_dir / "scripts" / module
            assert dest in written
            assert dest.read_text() == (REAL_SRC_DIR / module).read_text()

    def test_never_touches_a_hand_authored_assessment_py(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "draft-privacy-impact-assessment"
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(parents=True)
        hand_authored = scripts_dir / "assessment.py"
        hand_authored.write_text("# hand-authored, not synced from src/\n")

        written = sync_skill_scripts(skill_dir, REAL_SRC_DIR)

        assert hand_authored not in written
        assert hand_authored.read_text() == "# hand-authored, not synced from src/\n"

    def test_is_idempotent(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "draft-privacy-impact-assessment"
        first = {p: p.read_text() for p in sync_skill_scripts(skill_dir, REAL_SRC_DIR)}
        second = {p: p.read_text() for p in sync_skill_scripts(skill_dir, REAL_SRC_DIR)}
        assert first == second

    def test_modules_param_restricts_which_modules_are_copied(self, tmp_path: Path) -> None:
        # A rubric-less, triage-shaped skill (build-plan.md step 12) passes
        # a narrower module list to exclude rubric.py, which has nothing to
        # parse there.
        skill_dir = tmp_path / "triage-privacy-rights-request"
        written = sync_skill_scripts(skill_dir, REAL_SRC_DIR, ["concision.py", "language.py"])

        names = {p.name for p in written}
        assert names == {"concision.py", "language.py"}
        assert not (skill_dir / "scripts" / "rubric.py").exists()
        assert not (skill_dir / "scripts" / "report.py").exists()


class TestRenderFamilyManifestMarkdown:
    def test_includes_every_skill_with_its_domain_status_and_trigger(self) -> None:
        manifest = {
            "skills": [
                {
                    "name": "draft-privacy-impact-assessment",
                    "domain": "privacy",
                    "status": "built",
                    "trigger": "starting something that collects personal data",
                },
                {
                    "name": "assess-ai-system-risk-tier",
                    "domain": "ai-governance",
                    "status": "planned",
                    "trigger": "deploying a new AI system",
                },
            ]
        }
        markdown = render_family_manifest_markdown(manifest)
        assert "draft-privacy-impact-assessment" in markdown
        assert "assess-ai-system-risk-tier" in markdown
        assert "planned" in markdown
        assert "built" in markdown


class TestSyncRouterReferences:
    def test_writes_a_rendered_manifest_into_router_references(self, tmp_path: Path) -> None:
        manifest_path = tmp_path / "family-manifest.yaml"
        _write_yaml(
            manifest_path,
            {
                "skills": [
                    {
                        "name": "draft-privacy-impact-assessment",
                        "domain": "privacy",
                        "status": "built",
                        "trigger": "starting something that collects personal data",
                    }
                ]
            },
        )
        router_dir = tmp_path / "catholic-privacy-and-ai-governance"
        written = sync_router_references(router_dir, manifest_path)

        dest = router_dir / "references" / "family-manifest.md"
        assert written == [dest]
        assert "draft-privacy-impact-assessment" in dest.read_text()


class TestSyncAll:
    def test_returns_empty_when_no_manifest_exists(self, tmp_path: Path) -> None:
        # Sync must degrade gracefully, not error, in a project with no
        # family-manifest.yaml at all.
        assert sync_all(tmp_path, router_name="catholic-privacy-and-ai-governance") == []

    def test_succeeds_against_the_real_project_today(self) -> None:
        # As of build sequence step 9: one built skill (the flagship) and
        # the router, both with real folders — sync_all must succeed
        # without ManifestDriftError and sync both.
        written = sync_all(REPO_ROOT, router_name="catholic-privacy-and-ai-governance")
        relative = {p.relative_to(REPO_ROOT) for p in written}
        assert (
            Path(".claude/skills/draft-privacy-impact-assessment/references/frameworks/index.md")
            in relative
        )
        assert (
            Path(".claude/skills/draft-privacy-impact-assessment/scripts/language.py") in relative
        )
        assert (
            Path(".claude/skills/catholic-privacy-and-ai-governance/references/family-manifest.md")
            in relative
        )

    def _project_with_one_built_skill(self, tmp_path: Path) -> Path:
        frameworks_dir = tmp_path / "frameworks"
        frameworks_dir.mkdir()
        shutil.copy(REAL_FRAMEWORKS_DIR / "schema.yaml", frameworks_dir / "schema.yaml")
        _write_yaml(
            frameworks_dir / "index.yaml",
            {
                "frameworks": [
                    {
                        "id": "privacy-one",
                        "name": "Privacy One",
                        "type": "law",
                        "domain": "privacy",
                        "file": "privacy/privacy-one.yaml",
                        "status": "active",
                    }
                ]
            },
        )
        _write_yaml(
            frameworks_dir / "privacy" / "privacy-one.yaml",
            _framework_content("privacy-one", "Privacy One"),
        )

        rubric_dir = tmp_path / "rubric"
        rubric_dir.mkdir()
        (rubric_dir / "criteria.md").write_text(
            "## How to score\n\n- **Passing threshold: 4.**\n\n"
            "## 1. Widget quality — `widget-quality`\n"
        )

        _write_yaml(
            tmp_path / "family-manifest.yaml",
            {
                "skills": [
                    {
                        "name": "draft-privacy-impact-assessment",
                        "domain": "privacy",
                        "status": "built",
                        "rubric": "rubric/criteria.md",
                        "trigger": "starting something that collects personal data",
                    },
                    {
                        "name": "assess-ai-system-risk-tier",
                        "domain": "ai-governance",
                        "status": "planned",
                        "rubric": "rubric/criteria.md",
                        "trigger": "deploying a new AI system",
                    },
                ]
            },
        )
        (tmp_path / ".claude" / "skills" / "draft-privacy-impact-assessment").mkdir(parents=True)
        (tmp_path / ".claude" / "skills" / "catholic-privacy-and-ai-governance").mkdir(parents=True)
        return tmp_path

    def test_syncs_built_skills_and_the_router_skips_planned_ones(self, tmp_path: Path) -> None:
        project_root = self._project_with_one_built_skill(tmp_path)
        written = sync_all(
            project_root, router_name="catholic-privacy-and-ai-governance", src_dir=REAL_SRC_DIR
        )

        skills_dir = project_root / ".claude" / "skills"
        built_skill_dir = skills_dir / "draft-privacy-impact-assessment"
        built_index = built_skill_dir / "references" / "frameworks" / "index.md"
        router_manifest = (
            skills_dir / "catholic-privacy-and-ai-governance" / "references" / "family-manifest.md"
        )
        assert built_index in written
        assert router_manifest in written
        assert "assess-ai-system-risk-tier" not in built_index.read_text()
        assert (
            "assess-ai-system-risk-tier" in router_manifest.read_text()
        )  # router menu still lists it as planned
        assert not (skills_dir / "assess-ai-system-risk-tier").exists()  # never synced — not built

        for module in STDLIB_ONLY_MODULES:
            dest = built_skill_dir / "scripts" / module
            assert dest in written
            assert dest.read_text() == (REAL_SRC_DIR / module).read_text()

    def test_raises_when_a_built_entry_has_no_matching_skill_folder(self, tmp_path: Path) -> None:
        project_root = self._project_with_one_built_skill(tmp_path)
        shutil.rmtree(project_root / ".claude" / "skills" / "draft-privacy-impact-assessment")

        with pytest.raises(ManifestDriftError, match="draft-privacy-impact-assessment"):
            sync_all(project_root, router_name="catholic-privacy-and-ai-governance")

    def test_each_built_skill_syncs_against_its_own_manifest_rubric(self, tmp_path: Path) -> None:
        # Added at build sequence step 11: a second rubric (rubric/ai-criteria.md)
        # first existed alongside rubric/criteria.md here, so sync_all can no
        # longer assume every skill shares one global rubric path.
        project_root = self._project_with_one_built_skill(tmp_path)
        (project_root / "rubric" / "ai-criteria.md").write_text(
            "## How to score\n\n- **Passing threshold: 4.**\n\n"
            "## 1. Widget safety — `widget-safety`\n"
        )
        manifest_path = project_root / "family-manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text())
        manifest["skills"][1]["status"] = "built"  # assess-ai-system-risk-tier
        manifest["skills"][1]["rubric"] = "rubric/ai-criteria.md"
        _write_yaml(manifest_path, manifest)
        (project_root / ".claude" / "skills" / "assess-ai-system-risk-tier").mkdir(parents=True)

        sync_all(
            project_root, router_name="catholic-privacy-and-ai-governance", src_dir=REAL_SRC_DIR
        )

        skills_dir = project_root / ".claude" / "skills"
        privacy_rubric = (
            skills_dir / "draft-privacy-impact-assessment" / "references" / "rubric" / "criteria.md"
        ).read_text()
        ai_rubric = (
            skills_dir / "assess-ai-system-risk-tier" / "references" / "rubric" / "ai-criteria.md"
        ).read_text()
        assert "widget-quality" in privacy_rubric
        assert "widget-quality" not in ai_rubric
        assert "widget-safety" in ai_rubric
        assert "widget-safety" not in privacy_rubric

    def test_a_rubric_null_entry_syncs_with_no_rubric_at_all(self, tmp_path: Path) -> None:
        # A triage-shaped skill (build sequence step 12) has no rubric to
        # score against — `rubric: null` in the manifest must be
        # distinguished from the key being absent (which falls back to the
        # default rubric), not treated the same way.
        project_root = self._project_with_one_built_skill(tmp_path)
        manifest_path = project_root / "family-manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text())
        manifest["skills"].append(
            {
                "name": "triage-privacy-rights-request",
                "domain": "privacy",
                "status": "built",
                "rubric": None,
                "trigger": "a data subject rights request has arrived",
            }
        )
        _write_yaml(manifest_path, manifest)
        (project_root / ".claude" / "skills" / "triage-privacy-rights-request").mkdir(parents=True)

        sync_all(
            project_root, router_name="catholic-privacy-and-ai-governance", src_dir=REAL_SRC_DIR
        )

        triage_skill_dir = project_root / ".claude" / "skills" / "triage-privacy-rights-request"
        assert not (triage_skill_dir / "references" / "rubric").exists()
        assert (triage_skill_dir / "references" / "frameworks" / "index.md").exists()
        assert not (triage_skill_dir / "scripts" / "rubric.py").exists()
        assert (triage_skill_dir / "scripts" / "concision.py").exists()
