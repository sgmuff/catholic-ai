from pathlib import Path

import pytest
import yaml

from eval.principles import (
    load_non_negotiables,
    load_non_negotiables_grounding,
    load_principles,
)

_VALID_PRINCIPLE = {
    "id": "solidarity",
    "name": "Solidarity",
    "magisterial_citations": [
        {"source": "Compendium of the Social Doctrine of the Church", "reference": "§192-196"},
    ],
    "description": "A firm and persevering determination to commit oneself to the common good.",
    "tensions": [],
    "scenarios": [],
}

_VALID_NON_NEGOTIABLES = {
    "grounding": [
        {"source": "Compendium of the Social Doctrine of the Church", "reference": "§155"},
        {"source": "Magnifica Humanitas", "reference": "§55"},
    ],
    "items": [
        {
            "id": "direct-abortion",
            "title": "Direct (elective/procured) abortion",
            "description": "An AI use that facilitates or carries out a direct abortion.",
        },
        {
            "id": "euthanasia-or-assisted-suicide",
            "title": "Euthanasia or assisted suicide",
            "description": "An AI use that facilitates or carries out ending a person's life.",
        },
    ],
}


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data))


def test_load_principles_happy_path(tmp_path: Path):
    _write_yaml(tmp_path / "solidarity.yaml", _VALID_PRINCIPLE)
    _write_yaml(tmp_path / "schema.yaml", {"id": "string"})  # ignored, not a principle

    principles = load_principles(tmp_path)

    assert set(principles) == {"solidarity"}
    assert principles["solidarity"].name == "Solidarity"
    assert principles["solidarity"].citations[0].reference == "§192-196"


def test_load_principles_ignores_non_negotiables_file(tmp_path: Path):
    _write_yaml(tmp_path / "solidarity.yaml", _VALID_PRINCIPLE)
    _write_yaml(tmp_path / "non-negotiables.yaml", _VALID_NON_NEGOTIABLES)

    principles = load_principles(tmp_path)

    assert set(principles) == {"solidarity"}


def test_load_principles_raises_on_missing_field(tmp_path: Path):
    incomplete = dict(_VALID_PRINCIPLE)
    del incomplete["description"]
    _write_yaml(tmp_path / "solidarity.yaml", incomplete)

    with pytest.raises(ValueError, match="description"):
        load_principles(tmp_path)


def test_load_principles_raises_on_duplicate_id(tmp_path: Path):
    _write_yaml(tmp_path / "solidarity.yaml", _VALID_PRINCIPLE)
    _write_yaml(tmp_path / "solidarity-2.yaml", _VALID_PRINCIPLE)

    with pytest.raises(ValueError, match="duplicate principle id"):
        load_principles(tmp_path)


def test_load_principles_raises_on_non_mapping_file(tmp_path: Path):
    (tmp_path / "broken.yaml").write_text("- just\n- a\n- list\n")

    with pytest.raises(ValueError, match="expected a YAML mapping"):
        load_principles(tmp_path)


def test_load_non_negotiables_happy_path(tmp_path: Path):
    _write_yaml(tmp_path / "non-negotiables.yaml", _VALID_NON_NEGOTIABLES)

    items = load_non_negotiables(tmp_path)

    assert {i.id for i in items} == {"direct-abortion", "euthanasia-or-assisted-suicide"}


def test_load_non_negotiables_raises_on_duplicate_id(tmp_path: Path):
    data = {
        "grounding": _VALID_NON_NEGOTIABLES["grounding"],
        "items": [_VALID_NON_NEGOTIABLES["items"][0], _VALID_NON_NEGOTIABLES["items"][0]],
    }
    _write_yaml(tmp_path / "non-negotiables.yaml", data)

    with pytest.raises(ValueError, match="duplicate non-negotiable id"):
        load_non_negotiables(tmp_path)


def test_load_non_negotiables_raises_on_empty_items(tmp_path: Path):
    data = {"grounding": _VALID_NON_NEGOTIABLES["grounding"], "items": []}
    _write_yaml(tmp_path / "non-negotiables.yaml", data)

    with pytest.raises(ValueError, match="non-empty list"):
        load_non_negotiables(tmp_path)


def test_load_non_negotiables_grounding_happy_path(tmp_path: Path):
    _write_yaml(tmp_path / "non-negotiables.yaml", _VALID_NON_NEGOTIABLES)

    citations = load_non_negotiables_grounding(tmp_path)

    assert citations[0].source == "Compendium of the Social Doctrine of the Church"
    assert citations[1].reference == "§55"


def test_load_non_negotiables_grounding_raises_when_missing(tmp_path: Path):
    data = {"items": _VALID_NON_NEGOTIABLES["items"]}
    _write_yaml(tmp_path / "non-negotiables.yaml", data)

    with pytest.raises(ValueError, match="grounding"):
        load_non_negotiables_grounding(tmp_path)
