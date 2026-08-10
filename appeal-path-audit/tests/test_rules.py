from pathlib import Path

import pytest
import yaml

from appeal_path_audit.rules import load_rules

_VALID_RULE = {
    "id": "gdpr-art22-automation-disclosure",
    "framework": "GDPR Art. 22(3)",
    "description": "Notice must disclose that the decision was made by automated processing.",
    "severity": "high",
    "check": "keyword_presence",
    "check_args": {"required_substrings": ["automated"]},
}


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data))


def test_load_rules_happy_path(tmp_path: Path):
    _write_yaml(tmp_path / "gdpr.yaml", {"items": [_VALID_RULE]})

    rules = load_rules(tmp_path)

    assert set(rules) == {"gdpr-art22-automation-disclosure"}
    assert rules["gdpr-art22-automation-disclosure"].check == "keyword_presence"


def test_load_rules_raises_on_missing_field(tmp_path: Path):
    bad = dict(_VALID_RULE)
    del bad["severity"]
    _write_yaml(tmp_path / "bad.yaml", {"items": [bad]})

    with pytest.raises(ValueError, match="severity"):
        load_rules(tmp_path)


def test_load_rules_raises_on_invalid_severity(tmp_path: Path):
    bad = dict(_VALID_RULE)
    bad["severity"] = "extreme"
    _write_yaml(tmp_path / "bad.yaml", {"items": [bad]})

    with pytest.raises(ValueError, match="severity"):
        load_rules(tmp_path)


def test_load_rules_raises_on_unknown_check(tmp_path: Path):
    bad = dict(_VALID_RULE)
    bad["check"] = "vibes_check"
    _write_yaml(tmp_path / "bad.yaml", {"items": [bad]})

    with pytest.raises(ValueError, match="unknown check"):
        load_rules(tmp_path)


def test_load_rules_raises_on_duplicate_id(tmp_path: Path):
    _write_yaml(tmp_path / "a.yaml", {"items": [_VALID_RULE]})
    _write_yaml(tmp_path / "b.yaml", {"items": [_VALID_RULE]})

    with pytest.raises(ValueError, match="duplicate rule id"):
        load_rules(tmp_path)


def test_load_rules_raises_on_empty_items(tmp_path: Path):
    _write_yaml(tmp_path / "empty.yaml", {"items": []})

    with pytest.raises(ValueError, match="non-empty list"):
        load_rules(tmp_path)


def test_load_rules_raises_on_non_mapping_file(tmp_path: Path):
    (tmp_path / "broken.yaml").write_text("- just\n- a\n- list\n")

    with pytest.raises(ValueError, match="expected a YAML mapping"):
        load_rules(tmp_path)
