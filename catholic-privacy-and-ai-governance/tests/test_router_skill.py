"""Covers the router skill's own metadata and its relationship to
family-manifest.yaml (build-plan.md §6). Live triggering — whether a real
agent actually activates this skill on a generic invocation and defers to
a specialist on a specific one — isn't something a unit test can prove; see
build-plan.md's step 9 note on how that was checked instead.
"""

import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
ROUTER_DIR = REPO_ROOT / ".claude" / "skills" / "catholic-privacy-and-ai-governance"
MANIFEST_PATH = REPO_ROOT / "family-manifest.yaml"


def _router_frontmatter() -> dict:
    text = (ROUTER_DIR / "SKILL.md").read_text(encoding="utf-8")
    _, front, _ = text.split("---", 2)
    return yaml.safe_load(front)


class TestRouterMetadata:
    def test_name_matches_the_containing_folder_and_the_project(self) -> None:
        assert _router_frontmatter()["name"] == ROUTER_DIR.name == REPO_ROOT.name

    def test_description_is_present_and_within_the_spec_limit(self) -> None:
        description = _router_frontmatter()["description"]
        assert description.strip()
        assert len(description) <= 1024

    def test_description_explicitly_excludes_already_specific_requests(self) -> None:
        # The near-miss guard from build-plan.md §6.1 — without this, the
        # router risks false-triggering ahead of a specialist skill.
        description = _router_frontmatter()["description"].lower()
        assert "do not use this for a request that already clearly names" in description

    def test_plugin_json_name_matches_the_skill(self) -> None:
        plugin = json.loads((ROUTER_DIR / ".claude-plugin" / "plugin.json").read_text())
        assert plugin["name"] == ROUTER_DIR.name

    def test_skill_md_stays_under_the_repo_size_discipline(self) -> None:
        # docs/standards/skills.md: keep SKILL.md under ~500 lines.
        lines = (ROUTER_DIR / "SKILL.md").read_text(encoding="utf-8").splitlines()
        assert len(lines) < 500


class TestFamilyManifest:
    def _skills(self) -> list[dict]:
        return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))["skills"]

    def test_every_entry_has_a_unique_name(self) -> None:
        names = [s["name"] for s in self._skills()]
        assert len(names) == len(set(names))

    def test_every_entry_has_a_valid_domain_and_status(self) -> None:
        for skill in self._skills():
            assert skill["domain"] in {"privacy", "ai-governance"}
            assert skill["status"] in {"built", "planned", "retired"}
            assert skill["trigger"].strip()

    def test_every_built_entry_has_a_real_skill_folder(self) -> None:
        skills_dir = REPO_ROOT / ".claude" / "skills"
        for skill in self._skills():
            if skill["status"] == "built":
                assert (skills_dir / skill["name"]).is_dir(), (
                    f"{skill['name']} is marked built but has no folder"
                )

    def test_exactly_thirteen_skills_are_built_so_far(self) -> None:
        # Both flagships (step 11), draft-privacy-notice-update (step 12),
        # triage-privacy-rights-request (step 12 continued, the first
        # rubric-less/triage-shaped skill), triage-privacy-incident
        # (step 14, a sibling shape with parallel notification obligations
        # instead of a single governing deadline), triage-ai-incident
        # (step 15, reusing step 14's shape directly for a second domain),
        # review-vendor-privacy-assessment / review-ai-vendor-governance
        # (step 16, a fourth shape — a per-item baseline check — reused
        # across both domains), draft-model-card (step 17, sharing
        # assess-ai-system-risk-tier's exact rubric-scored shape, the way
        # draft-privacy-notice-update shares its own sibling's), and the
        # retention/verdict and regulatory-change shapes' four skills
        # (step 18: review-data-retention-entry, review-ai-system-
        # reassessment, map-regulatory-change, map-ai-regulatory-change)
        # — draft-ai-risk-impact-assessment is retired, not planned; the
        # backlog is otherwise empty.
        built = {s["name"] for s in self._skills() if s["status"] == "built"}
        assert built == {
            "draft-privacy-impact-assessment",
            "assess-ai-system-risk-tier",
            "draft-privacy-notice-update",
            "triage-privacy-rights-request",
            "triage-privacy-incident",
            "triage-ai-incident",
            "review-vendor-privacy-assessment",
            "draft-model-card",
            "review-ai-vendor-governance",
            "review-data-retention-entry",
            "review-ai-system-reassessment",
            "map-regulatory-change",
            "map-ai-regulatory-change",
        }

    def test_every_entry_with_a_rubric_field_points_at_a_real_file(self) -> None:
        # A triage-shaped skill's `rubric` is explicitly null — there's no
        # rubric for it to score against — so only non-null entries are
        # checked against the filesystem.
        for skill in self._skills():
            if skill["rubric"] is None:
                continue
            rubric_path = REPO_ROOT / skill["rubric"]
            assert rubric_path.is_file(), f"{skill['name']}: {skill['rubric']} does not exist"
