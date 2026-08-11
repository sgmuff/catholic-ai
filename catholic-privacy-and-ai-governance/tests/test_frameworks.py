import datetime
from pathlib import Path

import pytest
import yaml

from privacy_and_ai_governance.frameworks import (
    FRESHNESS_THRESHOLD_DAYS,
    FrameworkRegistryError,
    active_frameworks,
    load_framework_registry,
    stale_frameworks,
    validate_against_schema,
)

REPO_FRAMEWORKS_DIR = Path(__file__).parent.parent / "frameworks"


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def _minimal_schema() -> dict:
    return {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "status": {"type": "string", "enum": ["active", "retired"]},
        },
    }


class TestValidateAgainstSchema:
    def test_valid_instance_has_no_errors(self) -> None:
        schema = _minimal_schema()
        errors = validate_against_schema({"id": "x", "name": "X"}, schema)
        assert errors == []

    def test_missing_required_field_is_reported(self) -> None:
        schema = _minimal_schema()
        errors = validate_against_schema({"id": "x"}, schema)
        assert any("name" in e for e in errors)

    def test_wrong_type_is_reported(self) -> None:
        schema = _minimal_schema()
        errors = validate_against_schema({"id": "x", "name": 123}, schema)
        assert any("name" in e for e in errors)

    def test_enum_violation_is_reported(self) -> None:
        schema = _minimal_schema()
        errors = validate_against_schema(
            {"id": "x", "name": "X", "status": "not-a-real-status"}, schema
        )
        assert any("status" in e for e in errors)

    def test_nested_object_and_array_are_validated(self) -> None:
        schema = {
            "type": "object",
            "required": ["items"],
            "properties": {
                "items": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["id"],
                        "properties": {"id": {"type": "string"}},
                    },
                }
            },
        }
        errors = validate_against_schema({"items": [{}]}, schema)
        assert any("id" in e for e in errors)

    def test_array_below_min_items_is_reported(self) -> None:
        schema = {
            "type": "object",
            "required": ["items"],
            "properties": {"items": {"type": "array", "minItems": 1, "items": {"type": "string"}}},
        }
        errors = validate_against_schema({"items": []}, schema)
        assert any("items" in e for e in errors)


class TestLoadFrameworkRegistry:
    def test_loads_the_real_authored_registry_cleanly(self) -> None:
        records = load_framework_registry(REPO_FRAMEWORKS_DIR)
        by_id = {r["id"]: r for r in records}
        assert "gdpr-dpia" in by_id  # step 2's original framework never disappears

        gdpr = by_id["gdpr-dpia"]
        assert gdpr["domain"] == "privacy"
        assert gdpr["type"] == "law"
        assert gdpr["status"] == "active"
        assert gdpr["citation_root"] == "GDPR Art. 35"
        assert len(gdpr["required_elements"]) == 10
        assert len(gdpr["terms_of_art"]) == 9

    def test_every_registered_framework_has_a_unique_id(self) -> None:
        records = load_framework_registry(REPO_FRAMEWORKS_DIR)
        ids = [r["id"] for r in records]
        assert len(ids) == len(set(ids))
        assert len(ids) >= 1

    def test_raises_when_index_references_missing_file(self, tmp_path: Path) -> None:
        _write_yaml(tmp_path / "schema.yaml", _minimal_schema())
        _write_yaml(
            tmp_path / "index.yaml",
            {"frameworks": [{"id": "ghost", "name": "Ghost", "file": "nope.yaml"}]},
        )
        with pytest.raises(FrameworkRegistryError, match="nope.yaml"):
            load_framework_registry(tmp_path)

    def test_raises_when_content_fails_schema_validation(self, tmp_path: Path) -> None:
        _write_yaml(tmp_path / "schema.yaml", _minimal_schema())
        _write_yaml(
            tmp_path / "index.yaml",
            {"frameworks": [{"id": "bad", "name": "Bad", "file": "bad.yaml"}]},
        )
        _write_yaml(tmp_path / "bad.yaml", {"id": "bad"})  # missing required "name"
        with pytest.raises(FrameworkRegistryError, match="name"):
            load_framework_registry(tmp_path)

    def test_raises_when_content_id_does_not_match_index_entry(self, tmp_path: Path) -> None:
        _write_yaml(tmp_path / "schema.yaml", _minimal_schema())
        _write_yaml(
            tmp_path / "index.yaml",
            {"frameworks": [{"id": "expected-id", "name": "X", "file": "x.yaml"}]},
        )
        _write_yaml(tmp_path / "x.yaml", {"id": "different-id", "name": "X"})
        with pytest.raises(FrameworkRegistryError, match="id"):
            load_framework_registry(tmp_path)


class TestActiveFrameworks:
    def _records(self) -> list[dict]:
        return [
            {"id": "a", "domain": "privacy", "status": "active"},
            {"id": "b", "domain": "privacy", "status": "retired"},
            {"id": "c", "domain": "ai-governance", "status": "active"},
        ]

    def test_filters_out_retired_entries(self) -> None:
        result = active_frameworks(self._records())
        ids = {r["id"] for r in result}
        assert ids == {"a", "c"}

    def test_filters_by_domain_when_given(self) -> None:
        result = active_frameworks(self._records(), domain="privacy")
        ids = {r["id"] for r in result}
        assert ids == {"a"}


class TestStaleFrameworks:
    def test_recently_reviewed_entry_is_not_stale(self) -> None:
        today = datetime.date(2026, 8, 11)
        records = [{"id": "fresh", "last_reviewed": today}]
        assert stale_frameworks(records, today=today) == []

    def test_entry_just_under_the_threshold_is_not_stale(self) -> None:
        today = datetime.date(2026, 8, 11)
        last_reviewed = today - datetime.timedelta(days=FRESHNESS_THRESHOLD_DAYS)
        records = [{"id": "borderline", "last_reviewed": last_reviewed}]
        assert stale_frameworks(records, today=today) == []

    def test_entry_past_the_threshold_is_stale(self) -> None:
        today = datetime.date(2026, 8, 11)
        last_reviewed = today - datetime.timedelta(days=FRESHNESS_THRESHOLD_DAYS + 1)
        records = [{"id": "stale", "last_reviewed": last_reviewed}]
        result = stale_frameworks(records, today=today)
        assert [r["id"] for r in result] == ["stale"]

    def test_accepts_last_reviewed_as_an_iso_string_too(self) -> None:
        today = datetime.date(2026, 8, 11)
        records = [{"id": "string-date", "last_reviewed": "2020-01-01"}]
        result = stale_frameworks(records, today=today)
        assert [r["id"] for r in result] == ["string-date"]

    def test_the_real_registry_has_nothing_stale_today(self) -> None:
        records = load_framework_registry(REPO_FRAMEWORKS_DIR)
        assert stale_frameworks(records) == []
